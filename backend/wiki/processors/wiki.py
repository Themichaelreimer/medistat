import os, time
import requests
import re

from typing import List, Dict, Union
from bs4 import BeautifulSoup

from wiki.models import Article

BASE_PAGE = "https://en.wikipedia.org/wiki/List_of_diseases_({})"
PAGES = "0-9,A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z".split(",")
CRAWL_SLEEP_TIME = 4.0


def get_page(url: str) -> str:
    """Returns a page's html"""
    time.sleep(CRAWL_SLEEP_TIME)
    page = requests.get(url)
    if page.status_code == 200:
        return page.text
    return ""


def is_link_valid(href: str) -> bool:
    # Nav Link
    if "#" in href:
        return False
    # Classes of articles that are likely to be linked, but we don't want
    if "List_of_diseases" in href or "Outline_of" in href or "Category:" in href:
        return False
    # Articles that are linked but do not exist
    if "redlink=1" in href:
        return False
    return True


def pre_process_string(text: str) -> str:
    """
    Preprocesses text by stripping spaces, lowercasing, and removing wiki citation brackets [0][1]
    :param text: input
    :return: output
    """
    text = text.strip().lower()
    return re.sub(r"(\[.*\])", r"", text)


def get_links_from_page(html: str) -> List[str]:
    """Returns a list of links from a page"""
    result = []
    soup = BeautifulSoup(html, features="html.parser")

    links = soup.find("div", {"id": "content"}).findChildren("a")  # type:ignore[union-attr]
    for link in links:
        href = link.get("href")
        if href and is_link_valid(href):
            result.append("https://en.wikipedia.org" + href)
    return result


def get_title(html: str) -> str:
    """Returns the title of an article"""
    soup = BeautifulSoup(html, features="html.parser")
    h1 = soup.find("h1", {"id": "firstHeading"})
    if h1:
        return h1.text.strip()
    return ""


def save_webpage(name: str, html: str) -> None:
    """Saves html with a given file name"""
    article, created = Article.objects.update_or_create(defaults={"title": name}, text=html)


def get_infobox(html: str) -> Dict[str, str]:
    soup = BeautifulSoup(html, features="html.parser")
    data = {}
    tables = soup.find_all("table", {"class": "infobox"})
    for table in tables:
        for row in table.findChildren("tr"):
            header = row.findChildren("th")
            if header:
                header = header[0].text.lower()

                """
                if header == "classification":
                    # Extracts ICD-10 class
                    text = row.text
                    toks = text.split("ICD")
                    if len(toks) > 1:
                        token = toks[1]
                        if ":" in token:
                            data["ICD-10"] = token.split(":")[1].strip()
                """

            value = row.findChildren("td")
            if value:
                value = pre_process_string(value[0].text)

            if header and value:
                data[header] = value

    return data


def is_float(text: str) -> bool:
    try:
        float(text)
        return True
    except:
        return False


def is_int(text: str) -> bool:
    try:
        int(text)
        return True
    except:
        return False


def combine_adjacent_numbers(tokens: List[str]) -> List[str]:
    """
    Given a list of tokens, if any two adjacent tokens are numbers, they are combined by multiplication
    :param tokens: Tokenized string
    :return: Tokenized string, with the above property
    """
    result = []
    skip_next = False
    for i, token in enumerate(tokens):
        if skip_next:
            skip_next = False
            continue

        if i + 1 < len(tokens) and is_float(token) and is_float(tokens[i + 1]):
            result.append(float(token) * float(tokens[i + 1]))
            skip_next = True
        else:
            result.append(token)

    return result


def try_recognise_ratio(text: str) -> Union[float, None]:
    """
    If a ratio can be recognised in the input string, that ratio is returned. None otherwise
    :param text: input
    :return: float representing the ratio if detected, None otherwise
    """
    # Maybe use this regex? \d+\.?\d* ?(per|\/)? ?\d+

    input = re.sub(r",|'", r"", pre_process_string(text))
    input = re.sub(r"thousand", r"1000 ", input)
    input = re.sub(r"million", r"1000000 ", input)
    input = re.sub(r"billion", r"1000000000 ", input)
    input = re.sub(r"%", r" / 100", input)  # Causes "30%" -> "30 / 100" -> 0.3, interpreted as a ratio

    tokens = [x for x in input.split()]

    # Multiplies adjacent numbers and combines the tokens, eg ['2', '1000', 'per' 'year' -> '2000', 'per', 'year']
    tokens = combine_adjacent_numbers(tokens)

    numerator = None
    should_divide = False

    for token in tokens:
        if token in ["per", "/", "in"]:
            should_divide = True
            continue
        if is_float(token):
            if not numerator:
                numerator = token
            elif should_divide:
                denominator = token
                return float(numerator) / float(denominator)  # Greedy detect first fraction

    if numerator:
        if is_int(numerator):
            return int(numerator)
        return float(numerator)


def main() -> None:
    for PAGE_ID in PAGES:
        url = BASE_PAGE.format(PAGE_ID)
        index_html = get_page(url)
        links = get_links_from_page(index_html)

        for link in links:
            try:
                page_html = get_page(link)
                name = get_title(page_html)
                if name:
                    save_webpage(name, page_html)
            except Exception as e:
                print("===========================================")
                print(f"EXCEPTION ON LINK: <{link}>")
                print(e)
                print("===========================================")


if __name__ == "__main__":
    main()
