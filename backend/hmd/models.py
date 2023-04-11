from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.forms import model_to_dict

SEX_CHOICES = [("m", "m"), ("f", "f"), ("a", "a")]


class Country(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=8)

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


class MortalitySource(models.Model):
    name = models.CharField(max_length=64, null=False)
    link = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["name"])]


class MortalitySeries(models.Model):
    country = models.ForeignKey(Country, null=True, on_delete=models.SET_NULL)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, default="a")
    age = models.IntegerField()
    tags = ArrayField(
        models.IntegerField(), verbose_name=("choices")
    )  # Arrayfield is postgres exclusive. Can't have array of foreign keys, must settle for ints
    source = models.ForeignKey(MortalitySource, on_delete=models.CASCADE)

    class Meta:
        indexes = [models.Index(fields=["tags", "country", "sex", "age"])]


class MortalityDatum(models.Model):
    series = models.ForeignKey(MortalitySeries, on_delete=models.CASCADE)
    date = models.DateField()
    value = models.DecimalField(max_digits=12, decimal_places=6)

    class Meta:
        indexes = [models.Index(fields=["series", "-date"])]
