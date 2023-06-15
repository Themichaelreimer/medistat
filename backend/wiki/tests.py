from django.test import TestCase, SimpleTestCase

from wiki import query  # System under test
from wiki.processors import wiki as wiki_processor

from django.core.cache import cache
import requests
from typing import Optional


def try_get_article_text(url: str) -> Optional[str]:
    """
    Tries to fetch a page for testing against real data. Tests should skip portions that rely on the result of this function
    if this function returns None. It will return None if we cannot access the resource.

    Note that the results of this function are cached, so there is no reason to avoid calling this many times.
    """
    cache_key = "WIKIPEDIA_SAMPLE_ARTICLE"
    if result := cache.get(cache_key):
        return result

    req = requests.get(url)
    if req.status_code == 200:
        result = req.text
        cache.set(cache_key, result)
        return result


class QueryTests(TestCase):
    def setUp(self):
        pass


class ProcessorTests(TestCase):
    # If available, we will occasionally try to test parsing some real html.
    # The relevent sections of these tests should skip if real_article_html is None,
    # because the pipeline shouldn't fail over external availability
    SAMPLE_ARTICLE_LINK = "https://en.wikipedia.org/wiki/Influenza"
    real_article_html = try_get_article_text(SAMPLE_ARTICLE_LINK)

    def setUp(self) -> None:
        pass

    def test_get_title(self) -> None:
        html1 = """
        <html>
            <body>
                <h1 id='firstHeading'>
                    Boneitis
                </h1>
            </body>
        </html>
        """

        # Wrong tag
        html2 = """
        <html>
            <body>
                <h2 id='firstHeading'>
                    Boneitis
                </h1>
            </body>
        </html>
        """

        # Missing id
        html3 = """
        <html>
            <body>
                <h1>
                    Boneitis
                </h1>
            </body>
        </html>
        """

        # Two different h1 tags, but only one has the right id
        html4 = """
        <html>
            <body>
                <h1>
                    Tendonitis
                </h1>
                <p>
                    asdf
                </p>
                <h1 id='firstHeading'>
                    Boneitis
                </h1>
            </body>
        </html>
        """

        self.assertEqual(wiki_processor.get_title(html1), "Boneitis")
        self.assertEqual(wiki_processor.get_title(html2), "")
        self.assertEqual(wiki_processor.get_title(html3), "")
        self.assertEqual(wiki_processor.get_title(html4), "Boneitis")

        if self.real_article_html:
            self.assertEqual(wiki_processor.get_title(self.real_article_html), "Influenza")

    def test_pre_process_string(self):
        self.assertEqual(wiki_processor.pre_process_string(""), "")
        self.assertEqual(wiki_processor.pre_process_string("ASDF[1][2]"), "asdf")

    def test_combine_adjacent_numbers(self):
        # This function is used as an intermediate step in a text parsing pipeline,
        self.assertEquals(wiki_processor.combine_adjacent_numbers(["2", "1000", "deaths", "per", "year"]), [2000.0, "deaths", "per", "year"])

    def test_get_infobox(self) -> None:
        if self.real_article_html:
            print(wiki_processor.get_infobox(self.real_article_html))
