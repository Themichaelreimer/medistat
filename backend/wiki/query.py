from wiki.models import *
from typing import List


def get_nonempty_diseases() -> List[WikiDisease]:
    results = WikiDisease.objects.all()  # TODO
    return results
