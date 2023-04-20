from django.test import TestCase, SimpleTestCase
from django.conf import settings

import os, shutil, uuid
import datetime
from hashlib import md5

from datalake import helpers
from datalake.models import DataSource, RawData


class TestHelpers(SimpleTestCase):
    def test_clean_str(self) -> None:
        self.assertEquals(helpers.clean_str(""), "")
        self.assertEquals(helpers.clean_str("text123"), "text123")
        self.assertEquals(helpers.clean_str("TEXT"), "text")
        self.assertEquals(helpers.clean_str("text&^%123"), "text123")
        self.assertEquals(helpers.clean_str("!"), "")
        self.assertEquals(helpers.clean_str("text text"), "texttext")
        self.assertEquals(helpers.clean_str("text\tte,xt"), "texttext")


class TestModels(TestCase):
    # This folder will be created inside ./.tmp/ as a temporary datalake for the sake of testing
    datalake_folder_name = str(uuid.uuid4()).replace("-", "")
    datalake_home = os.path.join(os.getcwd(), ".tmp", datalake_folder_name)

    def setUp(self) -> None:
        return super().setUp()

    @classmethod
    def setUpClass(cls) -> None:
        super(TestModels, cls).setUpClass()

        # Setup a test directory and point the datalake towards that
        if not os.path.exists(cls.datalake_home):
            os.makedirs(cls.datalake_home)
            assert os.path.exists(cls.datalake_home)

        settings.DATALAKE_PATH = cls.datalake_home

    @classmethod
    def tearDownClass(cls) -> None:
        super(TestModels, cls).tearDownClass()
        shutil.rmtree(cls.datalake_home)

        assert not os.path.exists(cls.datalake_home)

    def test_store(self) -> None:
        file_data_1 = b"hi"
        file_md5 = md5(file_data_1).hexdigest()
        file_mtime = datetime.datetime(2022, 1, 2, tzinfo=datetime.timezone.utc)
        file_source = DataSource.objects.create(name="Test NGO")

        RawData.store(file_source, file_data_1, file_mtime)

        raw_data_record = RawData.objects.filter(source=file_source).first()

        self.assertEquals(raw_data_record.get_file_data(), file_data_1)
        self.assertEquals(raw_data_record.file_path, str(os.path.join(self.datalake_home, "testngo", "2022", "1", "2", file_md5)))
        self.assertEquals(raw_data_record.md5_hash, file_md5)
        self.assertEquals(raw_data_record.published_timestamp, file_mtime)
        self.assertEquals(raw_data_record.processed_timestamp, None)
