from django.db import models
from django.core.cache import cache
from django.contrib.postgres.fields import ArrayField
from django.forms import model_to_dict
from datalake.models import RawData

from typing import List

from hmd import helpers

SEX_CHOICES = [("m", "m"), ("f", "f"), ("a", "a")]


class Country(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        indexes = [models.Index(fields=["name"])]

    def __str__(self) -> str:
        return str(self.name)


# Populated by COUNTRY/STATS/fltper_1x1.txt or mltper_1x1.txt
# Deprecated, to be replaced by 2 MortalitySeries
class LifeTable(models.Model):
    country = models.ForeignKey(Country, null=True, on_delete=models.SET_NULL)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, default="a")
    age = models.IntegerField()
    year = models.IntegerField()
    probability = models.DecimalField(max_digits=10, decimal_places=5)
    cumulative_probability = models.DecimalField(max_digits=10, decimal_places=5)

    def __str__(self) -> str:
        return f"({self.age}{self.sex} {self.country}) - {self.probability}"

    def to_dict(self) -> dict:
        return {self.id: model_to_dict(self)}  # type:ignore


class MortalityTag(models.Model):
    name = models.CharField(max_length=64, null=False)

    class Meta:
        indexes = [models.Index(fields=["name"])]

    @staticmethod
    def quiet_get_or_create(name: str) -> "MortalityTag":
        """
        Identical to get_or_create, except it only returns the object and may be cached
        """
        key = f"mortality_tag_{name}"
        key = helpers.sanitize_cache_key(key)
        if res := cache.get(key):
            return res

        res, _ = MortalityTag.objects.get_or_create(name=name)

        cache.set(key, res)
        return res


class MortalitySeries(models.Model):
    tags = ArrayField(
        models.IntegerField(), verbose_name=("choices")
    )  # Arrayfield is postgres exclusive. Can't have array of foreign keys, must settle for ints

    class Meta:
        indexes = [models.Index(fields=["tags"])]

    @staticmethod
    def quiet_get_or_create(tag_names: List[str]) -> "MortalitySeries":
        tag_names.sort()
        key = f'mortality_series_{",".join([t for t in tag_names])}'
        key = helpers.sanitize_cache_key(key)
        if res := cache.get(key):
            return res

        tags = [MortalityTag.quiet_get_or_create(t).id for t in tag_names]
        res, _ = MortalitySeries.objects.get_or_create(tags=tags)

        cache.set(key, res)
        return res


# Represents an element of a nxm matrix, where n or m may be 1
class MortalityDatum(models.Model):
    age = models.IntegerField(null=True)
    series = models.ForeignKey(MortalitySeries, on_delete=models.CASCADE)
    date = models.DateField()
    value = models.DecimalField(max_digits=18, decimal_places=9)
    raw_data = models.ForeignKey(RawData, null=True, on_delete=models.CASCADE)

    class Meta:
        indexes = [models.Index(fields=["series", "-date"])]
