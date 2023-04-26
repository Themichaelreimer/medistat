from django.test import TestCase, SimpleTestCase
from django.utils import timezone

import os, importlib
import datetime
from types import ModuleType
from typing import Optional, Iterable, List, Set
from decimal import Decimal

from datalake.models import RawData, DataSource
from hmd.models import MortalityDatum, MortalitySeries, MortalityTag
from hmd.collectors import hmd as hmd_collector


class TestGeneralCollectors(SimpleTestCase):
    COLLECTORS_DIRECTORY = "hmd/collectors"

    def test_architecture(self) -> None:
        """
        Ensures that all collectors implement ETL by supporting seperate extract and transform steps, callable in a consistent way.
        There is no seperate load step, since it would be the same one line of code in every data source, and it would add complexity without benefit.
        Therefore, the expectation is that the Transform step loads after processing.
        """

        def __test_collector_module(module: ModuleType) -> None:
            """
            Tests that a particular file implements the interface correctly.
            Raises exception on any interface violations.
            """
            self.assertIn("extract", dir(module), f"module {module} must implement a function extract() -> bool")
            self.assertIn("transform", dir(module), f"module {module} must implement a function transform() -> int")

            extract_annotations = module.extract.__annotations__
            transform_annotations = module.transform.__annotations__

            # Idea: static analysis performed elsewhere in the pipeline will force the function to actually return the types
            # that we annotate. So here, we force the correct annotations.
            self.assertEquals(extract_annotations, {"return": bool})
            self.assertEquals(transform_annotations, {"raw_data": Optional[Iterable[RawData]], "return": int})

        files = [x for x in os.listdir(self.COLLECTORS_DIRECTORY) if x[-3:] == ".py" and x[:2] != "__"]
        collectors = ["".join(file.split(".")[:-1]) for file in files]
        collectors.sort()

        for collector in collectors:
            collector_module = importlib.import_module(f"hmd.collectors.{collector}")
            __test_collector_module(collector_module)


class TestModelMethods(TestCase):
    def test_mortality_series__get_or_create(self) -> None:
        tags = ["Male", "Births", "Canada"]

        series = MortalitySeries.quiet_get_or_create(tags)
        queried_tag_names = MortalityTag.objects.filter(id__in=series.tags).values("name").order_by("id")
        queried_tag_names = [x["name"] for x in queried_tag_names]
        self.assertEquals(queried_tag_names, tags)


class TestHMDCollector(TestCase):
    # These tables are for testing the process_table parsing algorithm
    table_1 = """Bulgaria, Population size (abridged) Last modified: 15 Sep 2022;  Methods Protocol: v6 (2017)\n
\n
Year          Age             Female            Male           Total\n
1947           0             74629.57        78684.98       153314.55\n
2009          95               478.37          211.61          689.98\n
"""

    table_2 = """Australia, Life tables (period 1x1), Total Last modified: 29 Nov 2022;  Methods Protocol: v6 (2017)\n
\n
Year          Age         mx       qx    ax      lx      dx      Lx       Tx     ex\n
1921           0      0.06844  0.06522  0.28  100000    6522   95294  6097256  60.97\n
2001           3      0.00020  0.00020  0.50   99421      19   99411  7702925  77.48\n
"""

    def test_extract_row(self) -> None:
        row_1 = "  1765           1                    .               .               ."
        self.assertEquals(hmd_collector.extract_row(row_1), ["1765", "1", ".", ".", "."])

    def test_extract_file_header_data(self) -> None:
        row_1 = "Belgium, Exposure to risk (cohort 1x1), Last modified: 26 Dec 2022;  Methods Protocol: v6 (2017)"
        self.assertEquals(hmd_collector.extract_file_header_data(row_1), {"country": "Belgium", "dataset_name": "Exposure to risk"})

    def test_process_table_schema_1(self) -> None:
        def tags_array_to_tags_set(tag_ids: List[int]) -> Set[str]:
            queried_tag_names = MortalityTag.objects.filter(id__in=tag_ids).values("name").order_by("id")
            queried_tag_names = set(x["name"] for x in queried_tag_names)
            return queried_tag_names

        data_source = DataSource.objects.create(name="Data Source", link="https://fake.site")
        raw_data = RawData.store(data_source, self.table_1.encode("utf-8"), timezone.now(), "https://fake.site/dataset")

        num_records = hmd_collector.process_table(raw_data, "asdf", self.table_1)
        self.assertEquals(int, type(num_records), f"process_table should return an int; returned `{type(num_records)}`")

        dataset = list(MortalityDatum.objects.values("series__tags", "date", "age", "value").order_by("date"))
        for item in dataset:
            item["series__tags"] = tags_array_to_tags_set(item["series__tags"])

        self.assertEquals(
            dataset,
            [
                {
                    "series__tags": {"Bulgaria", "Population size", "Female"},
                    "date": datetime.date(year=1947, month=1, day=1),
                    "age": 0,
                    "value": Decimal("74629.57"),
                },
                {
                    "series__tags": {"Bulgaria", "Population size", "Male"},
                    "date": datetime.date(year=1947, month=1, day=1),
                    "age": 0,
                    "value": Decimal("78684.98"),
                },
                {
                    "series__tags": {"Bulgaria", "Population size", "Both sexes"},
                    "date": datetime.date(year=1947, month=1, day=1),
                    "age": 0,
                    "value": Decimal("153314.55"),
                },
                {
                    "series__tags": {"Bulgaria", "Population size", "Female"},
                    "date": datetime.date(year=2009, month=1, day=1),
                    "age": 95,
                    "value": Decimal("478.37"),
                },
                {
                    "series__tags": {"Bulgaria", "Population size", "Male"},
                    "date": datetime.date(year=2009, month=1, day=1),
                    "age": 95,
                    "value": Decimal("211.61"),
                },
                {
                    "series__tags": {"Bulgaria", "Population size", "Both sexes"},
                    "date": datetime.date(year=2009, month=1, day=1),
                    "age": 95,
                    "value": Decimal("689.98"),
                },
            ],
        )

    def test_process_table_schema_2(self) -> None:
        def tags_array_to_tags_set(tag_ids: List[int]) -> Set[str]:
            queried_tag_names = MortalityTag.objects.filter(id__in=tag_ids).values("name").order_by("id")
            queried_tag_names = set(x["name"] for x in queried_tag_names)
            return queried_tag_names

        data_source = DataSource.objects.create(name="Data Source", link="https://fake.site")
        raw_data = RawData.store(data_source, self.table_2.encode("utf-8"), timezone.now(), "https://fake.site/dataset")

        num_records = hmd_collector.process_table(raw_data, "blt.txt", self.table_2)  # blt.txt is the file name which implies both sexes
        self.assertEquals(int, type(num_records), f"process_table should return an int; returned `{type(num_records)}`")

        dataset = list(MortalityDatum.objects.values("series__tags", "date", "age", "value").order_by("date"))
        for item in dataset:
            item["series__tags"] = tags_array_to_tags_set(item["series__tags"])

        # This table will produce too many entries to make it practical to check every entry exactly.
        # So we will spot check the result and check that the number of results is accurate.
        self.assertIn(
            {
                "series__tags": {"Australia", "Life expectancy", "Both sexes", "Life tables"},
                "date": datetime.date(year=1921, month=1, day=1),
                "age": 0,
                "value": Decimal("60.97"),
            },
            dataset,
        )

        self.assertIn(
            {
                "series__tags": {"Australia", "Probability of surviving from birth", "Both sexes", "Life tables"},
                "date": datetime.date(year=2001, month=1, day=1),
                "age": 3,
                "value": Decimal("0.99421"),
            },
            dataset,
        )
