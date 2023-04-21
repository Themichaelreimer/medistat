from django.core.management.base import BaseCommand, CommandError, CommandParser
from types import ModuleType
from typing import List
import os, sys, importlib


class Command(BaseCommand):
    help = "This command manages data collection."
    COLLECTORS_DIRECTORY = "hmd/collectors"

    def add_arguments(self, parser: CommandParser) -> None:
        collector_names = self.get_supported_collectors()

        parser.add_argument(
            "layer", type=str, help="Layer of collector. Options are: [`extract`,`transform`,`all`]. `all` runs `extract` and then `transform`."
        )
        parser.add_argument("collector_name", type=str, help=f"Name of collector. Supported options are: {collector_names}")

    def handle(self, *args, **options) -> None:  # type:ignore
        print(sys.argv)

    @staticmethod
    def get_supported_collectors() -> List[str]:
        files = [x for x in os.listdir(Command.COLLECTORS_DIRECTORY) if x[-3:] == ".py" and x[:2] != "__"]
        collectors = ["".join(file.split(".")[:-1]) for file in files]
        collectors.sort()
        return collectors

    def display_help(self, collectors: List[str]) -> None:
        print("Syntax: manage.py collect [extract|transform|all] [collector_name]")
        print(f"Where `collector_name` is one of: {collectors}")

    def run_module(self, module: ModuleType) -> None:
        extract = getattr(module, "extract")
        transform = getattr(module, "transform")

        if extract():
            transform()
