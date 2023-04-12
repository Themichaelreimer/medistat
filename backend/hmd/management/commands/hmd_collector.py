from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache

# Note: mypy CLI says it can't find the stubs for requests, even though they are installed and are also even successfully used in mypy typechecks
import requests  # type:ignore
from hmd.models import Country, LifeTable, MortalitySource, MortalitySeries, MortalityDatum

import os
import re
import zipfile
from io import BytesIO
from typing import List, Tuple, Optional

FILE_NAMES = ["fltper_1x1.txt", "mltper_1x1.txt"]
SOURCE_NAME = "Human Mortality Database"
SOURCE_LINK = "https://www.mortality.org/"

# NOTE: In order to use this collector, you MUST register with the Human Mortality Database and
# set your credentials to the following environment variables:
#
#   HMD_USERNAME="..."
#   HMD_PASSWORD="..."


def get_zipped_data(email: str, password: str) -> BytesIO:
    """
    Logs into the HMD website, downloads the zip file containing the current state of the dataset.
    The returned result is the zip file as an in-memory file
    :param email: Human Mortality Database email/username (They're the same thing in this context)
    :param password: Human Mortality Database password
    :return: zip file of their dataset, as an in-memory filezx
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
    result = BytesIO(zip_download.content)
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


def get_sex(file_name: str) -> Optional[str]:
    """
    returns m or f based on input, which should be a file name
    """
    if "flt" in file_name:
        return "f"
    if "mlt" in file_name:
        return "m"
    return None


class Command(BaseCommand):
    help = "Loads HMD life tables into database. Calculates cumulative along the way"

    SOURCE = MortalitySource

    def handle(self, *args, **options) -> None:  # type:ignore
        HMD_USERNAME = os.environ.get("HMD_USERNAME")
        HMD_PASSWORD = os.environ.get("HMD_PASSWORD")

        assert HMD_USERNAME, "Please set the `HMD_USERNAME` environment variable in order to continue"
        assert HMD_PASSWORD, "Please set the `HMD_PASSWORD` environment variable in order to continue"

        zip_data = get_zipped_data(HMD_USERNAME, HMD_PASSWORD)
        zip = zipfile.ZipFile(zip_data)

        for filename in zip.namelist():
            # All file names have a "nxm" in their name. These refer to the grouping of age brackets
            # We're only interested in the highest resolution version of the data, so we ignore all other groupings.
            if not "1x1" in filename:
                continue
            data = zip.open(filename).read().decode("utf-8")
            self.process_table(filename, data)

    def process_table(self, file_name: str, file_data: str) -> None:
        country_name = file_data[0].split(",")[0]
        country = self.ensure_country(country_name)
        sex = get_sex(file_name)

        for row_text in file_data[4:]:
            row = extract_row(row_text)
            year = row[0]
            age = row[1]

            probability = row[3]
            if probability == ".":
                probability = 100

            if row[5] == ".":
                p_alive: float = 0.0
            else:
                p_alive = int(row[5]) / 100000

            if "+" in age:
                age = age[0:-1]

            params = {
                "country": country,
                "sex": sex,
                "year": year,
                "age": age,
                "probability": probability,
                "cumulative_probability": p_alive,
            }

            self.ensure_life_table_entry(params)

    @staticmethod
    def ensure_country(country: str) -> Country:
        res, _ = Country.objects.get_or_create(name=country)
        return res

    @staticmethod
    def ensure_life_table_entry(params: dict) -> None:
        """
        Takes: country,sex,age,year,probability,cumulative_probability
        :param params: dict with the above keys
        :return: None
        """
        LifeTable.objects.get_or_create(**params)
