from django.core.cache import cache
from django.db import transaction

# Note: mypy CLI says it can't find the stubs for requests, even though they are installed and are also even successfully used in mypy typechecks
import requests  # type:ignore
from hmd.models import Country, LifeTable, MortalitySeries, MortalityDatum
from datalake.models import DataSource, RawData

import os
import re
import zipfile
from io import BytesIO
from typing import List, Tuple, Optional, Iterable
import datetime, dateparser  # type:ignore

FILE_NAMES = ["fltper_1x1.txt", "mltper_1x1.txt"]
SOURCE_NAME = "Human Mortality Database"
SOURCE_LINK = "https://www.mortality.org/"

# NOTE: In order to use this collector, you MUST register with the Human Mortality Database and
# set your credentials to the following environment variables:
#
#   HMD_USERNAME="..."
#   HMD_PASSWORD="..."

# Aliases to columns mentioned in the HMD tables. If a key appears, it is replaced with the vaulue during parsing
ALIASES = {"mx": "", "qx": "", "ax": "", "lx": "", "dx": "", "Lx": "", "Tx": "", "ex": ""}


# @transaction
def extract() -> bool:
    """
    Extracts data from the source and saves it unmodified in the data lake
    Returns whether there is new data.
    """

    HMD_USERNAME = os.environ.get("HMD_USERNAME")
    HMD_PASSWORD = os.environ.get("HMD_PASSWORD")

    assert HMD_USERNAME, "Please set the `HMD_USERNAME` environment variable in order to continue"
    assert HMD_PASSWORD, "Please set the `HMD_PASSWORD` environment variable in order to continue"

    source, _ = DataSource.objects.get_or_create(name=SOURCE_NAME, link=SOURCE_LINK)
    data_file, timestamp = get_zipped_data(HMD_USERNAME, HMD_PASSWORD)

    if not RawData.has_already(source, data_file):
        RawData.store(source, data_file, timestamp, SOURCE_LINK)
        return True
    return False


# @transaction
def transform(raw_data: Optional[Iterable[RawData]] = None) -> int:
    """
    Transforms raw data units into clean, structured data.
    Implicitly performs the "load" step of ETL at the end. This could have been made a seperate function, but
    it will be the same everywhere, and there is no practical benefit to seperating the load step in this pipeline.
    """

    if not raw_data:
        source = DataSource.objects.get(name=SOURCE_NAME)
        raw_data = RawData.get_unprocessed_data_by_source(source)

    for data_record in raw_data:
        zip = zipfile.ZipFile(BytesIO(data_record.get_file_data()))
        for filename in zip.namelist():
            # All file names have a "nxm" in their name. These refer to the grouping of age brackets
            # We're only interested in the highest resolution version of the data, so we ignore all other groupings.
            if not ".txt" in filename or not "1x1" in filename:
                continue
            data = zip.open(filename).read().decode("utf-8")
            process_table(data_record, filename, data)
        data_record.mark_as_processed()
    return 0


def get_zipped_data(email: str, password: str) -> Tuple[BytesIO, datetime.datetime]:
    """
    Logs into the HMD website, downloads the zip file containing the current state of the dataset.
    The returned result is the zip file as an in-memory file
    :param email: Human Mortality Database email/username (They're the same thing in this context)
    :param password: Human Mortality Database password
    :return: zip file of their dataset, as an in-memory file
    """
    CACHE_KEY = "hmd_bulk_data"
    if file_data := cache.get(CACHE_KEY):
        return file_data

    LOGIN_URL = "https://www.mortality.org/Account/Login"
    session = requests.Session()

    # Request the login page for CSRF reasons.
    req = session.get(LOGIN_URL)
    assert req.status_code == 200, req.text
    csrf = extract_request_verification_token(req.text)

    data = {"Email": email, "Password": password, "ReturnURL": "https://www.mortality.org", "__RequestVerificationToken": csrf}

    req = session.post(LOGIN_URL, data=data)
    assert req.status_code == 200, req.text

    # This takes a good while. The file is ~160MB. We cache this in redis with a long lifetime in order to avoid
    # Unnecessarily repeating this long step
    zip_download = session.get("https://www.mortality.org/File/Download/hmd.v6/zip/all_hmd/hmd_statistics_20230403.zip")
    datetime_str = zip_download.headers["Date"]
    timestamp = dateparser.parse(datetime_str)

    result = (zip_download.content, timestamp)
    cache.set(CACHE_KEY, result, 24 * 3600)

    return result


def extract_request_verification_token(html: str) -> str:
    """
    Extracts the '__RequestVerificationToken' from the page html that contains it
    """
    # <input name="__RequestVerificationToken" type="hidden" value="CfDJ8AoeI-RjTIRIgpWOhbAlEC_WjcjX2-BxjVIEJNxNXdGc7kBsFnfDZsfx06CPrJxqHj9VOz-0-h-3Fz4EMHrQkoF8f0DtOuFDV7gwDJUsbSrOduStQrnTX5ecCpzYaLWpJP0A-nJF--nDLv3V6ibty0s" /></form>
    if match := re.search(r"<input name=\"__RequestVerificationToken\" type=\"hidden\" value=\"(\S*)\"", html):
        return match.group(1)
    raise Exception("Could not detect CSRF token inside html.")


def extract_row(text: str) -> list:
    return [x for x in text.split(" ") if x]


def extract_file_header_data(line: str) -> dict:
    """
    Extracts the useful information from the first line of a hmd data file
    into a dict with the keys: 'country', and 'dataset_name'
    :param line: The first line of a HMD data file
    :return: dict containing 'country' and 'dataset_name'
    """
    tokens = line.split(",")
    if len(tokens) < 2:
        return {}

    country = tokens[0].strip()
    dataset_name = tokens[1].split("(")[0].strip()  # This section looks like "Exposure to risk (cohort 1x1)"
    # tokens[2] would contain info on last modified. We also get the last modified time less accurately from the metadata.

    return {"country": country, "dataset_name": dataset_name}


def get_sex(file_name: str) -> Optional[str]:
    """
    returns m or f based on input, which should be a file name
    """
    if "flt" in file_name:
        return "Female"
    if "mlt" in file_name:
        return "Male"
    return None


def process_table(raw_data: RawData, file_name: str, file_data_str: str) -> None:
    file_data = file_data_str.split("\n")

    header_metadata = extract_file_header_data(file_data[0])

    # country = ensure_country(header_metadata['country'])
    dataset_name = header_metadata["dataset_name"]
    sex = get_sex(file_name)

    table_headers = None

    for row_text in file_data[1:]:
        row = extract_row(row_text)

        # If we haven't read the table header yet, and there is stuff in this row, assume it's the headers
        if not table_headers:
            if len(row) > 1:
                table_headers = row
                continue

        # Main parsing section: Read line, output statistics
        # NOTE:
        # - Wont always have sex. Sometimes must consult file_name
        # - Won't always have age. Some series don't have an age component (eg: Life expectancy at birth)

        dict_row = {x: y for x, y in zip(table_headers, row)}

        year = dict_row.get("Year")
        age = dict_row.get("Age")
        statistic_names = [x for x in dict_row.keys() if x not in ["Year", "Age"]]
        for statistic_name in statistic_names:
            entry_value = dict_row[statistic_name]

            if statistic_name in ALIASES:
                statistic_name = ALIASES[statistic_name]

            if statistic_name in ["Male", "Female"]:
                sex = statistic_name

        tags = [header_metadata["country"], sex, dataset_name]
        tags = [t for t in tags if t]

        if age is not None and "+" in age:
            age = age[0:-1]

        series = MortalitySeries.quiet_get_or_create(tags)
        datum = {}


def ensure_country(country: str) -> Country:
    res, _ = Country.objects.get_or_create(name=country)
    return res


def ensure_life_table_entry(params: dict) -> None:
    """
    Takes: country,sex,age,year,probability,cumulative_probability
    :param params: dict with the above keys
    :return: None
    """
    LifeTable.objects.get_or_create(**params)
