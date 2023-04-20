from django.db import models
from django.utils import timezone
from django.conf import settings

from typing import Union, Optional
import os
import datetime
from hashlib import md5
from pathlib import Path

from datalake import helpers


class DataSource(models.Model):
    name = models.CharField(max_length=64, null=False, unique=True)
    link = models.TextField(default="")

    class Meta:
        indexes = [models.Index(fields=["name"])]


class RawData(models.Model):
    source = models.ForeignKey(DataSource, on_delete=models.DO_NOTHING)
    published_timestamp = models.DateTimeField()  # Time data source published this document
    loaded_timestamp = models.DateTimeField(default=timezone.now)  # For audit purposes only; never a reason to override the default timestamp
    processed_timestamp = models.DateTimeField(null=True)  # For audit purposes only
    file_path = models.TextField()
    link = models.TextField(default="")  # Link to raw data, used to build references where available
    md5_hash = models.CharField(max_length=32)

    class Meta:
        indexes = [models.Index(fields=["source", "-processed_timestamp"]), models.Index(fields=["source", "md5_hash"])]

    @staticmethod
    def store(source: DataSource, raw_data: Union[str, bytes], published_timestamp: Optional[datetime.datetime] = None, link: str = "") -> None:
        # This block looks inefficient, but it looks this way to play nicely with static analysis
        if type(raw_data) == str:
            raw_data = raw_data.encode("utf-8")
            md5_digest = md5(raw_data).hexdigest()
        if type(raw_data) == bytes:
            md5_digest = md5(raw_data).hexdigest()
        else:
            raise Exception(f"Unexpected raw_data type in RawData.store. Expected [str,bytes], got {type(raw_data)}")

        # Ensure parent directory exists
        full_path = RawData.get_file_path(source, published_timestamp, md5_digest)
        path = Path(full_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "wb") as outfile:
            outfile.write(raw_data)

        RawData.objects.create(source=source, published_timestamp=published_timestamp, file_path=full_path, link=link, md5_hash=md5_digest)

    @staticmethod
    def has_already(source: DataSource, raw_data: Union[str, bytes]) -> bool:
        """
        Checks if we already have a piece of data, based on the md5 hex digest.
        :param source: Data Source
        :param raw_data: Data being imported
        :return: Whether this raw data is already stored in the database.
        """
        # This block looks inefficient, but it looks this way to play nicely with static analysis
        if type(raw_data) == bytes:
            return RawData.objects.filter(source=source, md5_hash=md5(raw_data).hexdigest()).exists()
        elif type(raw_data) == str:
            return RawData.objects.filter(source=source, md5_hash=md5(raw_data.encode("utf-8")).hexdigest()).exists()
        else:
            raise Exception(f"Unexpected raw_data type in RawData.has_already. Expected [str,bytes], got {type(raw_data)}")

    @staticmethod
    def get_file_path(source: DataSource, published_time: datetime.datetime, file_name: Union[os.PathLike, str]) -> str:
        """
        Returns the intended file path of a given raw data file being saved.
        :param source: Data Source
        :param published_time: published time of data source.
        :param file_name: Suggested filename. Generally this will be a truncated md5 str
        """
        return os.path.join(
            settings.DATALAKE_PATH,
            helpers.clean_str(source.name),
            str(published_time.year),
            str(published_time.month),
            str(published_time.day),
            file_name,
        )

    def get_file_data(self) -> bytes:
        with open(self.file_path, "rb") as f:
            return f.read()
