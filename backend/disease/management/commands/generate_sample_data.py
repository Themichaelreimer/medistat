from django.core.management.base import BaseCommand
from wiki.business import handle_infobox

import os
import json


class Command(BaseCommand):
    help = "Loads a small, quick dataset. Not terribly interesting, but excellent for testing purposes."
    file_name = os.path.join("disease", "metadata", "sample_data.json")

    def handle(self, *args, **options):
        sample_data = self.get_sample_data()
        for infobox in sample_data.get("infoBoxes", []):
            handle_infobox(infobox)

    @staticmethod
    def get_sample_data() -> dict:
        """
        Loads the contents of sample_data.json into a dictionary and returns the result
        """
        with open(Command.file_name) as file:
            contents = file.read()
            return json.loads(contents)
