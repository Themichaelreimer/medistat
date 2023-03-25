from django.test import TestCase

from wiki import query  # System under test


class WikiTests(TestCase):
    def setUp(self):
        pass

    def test_ensure_speciality_case(self):
        """
        Ensure speciality should force specialities to be saved/loaded in lower case
        """
        speciality_1 = query.ensure_speciality("Test")
        speciality_2 = query.ensure_speciality("test")
        self.assertEquals(
            speciality_1,
            speciality_2,
            "`Test` and `test` should create the same object",
        )
        self.assertEquals(speciality_1.name, "test", "`Test` should be stored as `test`")
