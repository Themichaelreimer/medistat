from django.test import TestCase, SimpleTestCase

import os, importlib
from types import ModuleType
from typing import Optional, Iterable

from datalake.models import RawData
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


class TestHMDCollector(SimpleTestCase):
    def test_extract_row(self) -> None:
        row_1 = "  1765           1                    .               .               ."
        self.assertEquals(hmd_collector.extract_row(row_1), ["1765", "1", ".", ".", "."])

    def test_extract_file_header_data(self) -> None:
        row_1 = "Belgium, Exposure to risk (cohort 1x1), \tLast modified: 26 Dec 2022;  Methods Protocol: v6 (2017)"
        self.assertEquals(hmd_collector.extract_file_header_data(row_1), {"country": "Belgium", "dataset_name": "Exposure to risk"})
