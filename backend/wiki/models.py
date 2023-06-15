from django.db import models
from decimal import Decimal

# Create your models here.
"""
    The models in this file are deprecated. From Phase2 and onwards, Diseases should be modeled
    using disease/models.py. The models there are more general and better fit a
    'multiple values from different sources' model
"""


class Article(models.Model):
    """
    This class represents an article post parsing HTML, but with no other processing yet
    """

    title = models.CharField(default="", max_length=128, unique=True)
    first_sentence = models.TextField(default="")
    text = models.TextField(default="")
    link = models.TextField(default="")
    disease = models.ForeignKey("WikiDisease", null=True, default=None, on_delete=models.SET_NULL)
    processed_timestamp = models.DateTimeField(null=True, default=None)

    class Meta:
        indexes = [
            models.Index(
                fields=["processed_timestamp"]
            )  # Used to tell what still needs to be processed - This is the only select query for this table
        ]


class Fact(models.Model):
    """
    This class represents a piece of non-timeseries information about a disease
    """

    disease = models.ForeignKey("WikiDisease", on_delete=models.CASCADE)
    fact_type = models.ForeignKey("FactType", on_delete=models.CASCADE)
    value = models.ForeignKey("FlexibleValue", on_delete=models.CASCADE)
    citation_text = models.TextField(default="")
    source_article = models.ForeignKey("Article", null=True, on_delete=models.SET_NULL)

    def to_dict(self) -> dict:
        return {
            "disease": self.disease.name,
            "fact_type": self.fact_type.name,
            "citation_text": self.citation_text,
            "article_link": self.source_article.link
            ** self.value.to_dict(),  # Adds the key-value pairs from the value's to_dict() to this dict to avoid nesting objects
        }

    class Meta:
        indexes = [models.Index(fields=["disease"]), models.Index(fields=["fact_type"]), models.Index(fields=["disease", "fact_type"])]


class FactType(models.Model):
    """
    The name of the kind of a kind of fact (usually a statistic). Eg, Symptoms, mortality rate, frequency, cases per year, etc.
    """

    name = models.CharField(max_length=127, unique=True)


class FlexibleValue(models.Model):
    """
    This class represents a value that can be reported in a fuzzy way that typically has meaning to humans, but poor computational meaning.
    Examples include:
        - 1,000,000
        - ~1,000,000
        - 500 to 1000
        - less than 5000

    The data model works like this:
        - Where a range of values is needed, populate min_range and max_range
        - Where a single value is needed, populate single_value
            - If a modifier is needed for a single value for more context, use modifier column. Options are: `<`, `>`, and `~`. Empty implies `=`.
        - Populate value type with single or range.

    """

    class ValueType(models.TextChoices):
        SINGLE = "single", "single value"
        RANGE = "range", "range value"
        STRING = "string", "string value"

    class Modifier(models.TextChoices):
        LESS_THAN = "<", "<"
        MORE_THAN = ">", ">"
        EXACTLY = "", ""
        ROUGHLY = "~", "~"

    single_value = models.DecimalField(max_digits=32, decimal_places=16, null=True, blank=True)
    string_value = models.TextField(null=True, blank=True)
    min_range = models.DecimalField(max_digits=32, decimal_places=16, null=True, blank=True)
    max_range = models.DecimalField(max_digits=32, decimal_places=16, null=True, blank=True)
    value_type = models.CharField(max_length=6, choices=ValueType.choices, default=ValueType.SINGLE)
    modifier = models.CharField(max_length=1, choices=Modifier.choices, default=Modifier.EXACTLY)

    def sorting_key(self) -> Decimal:
        """
        Returns a decimal intended to be used to sort values by, factoring in the flexibility of this data model.
        If the valuetype is a single value, then single_value is the key. Otherwise, the average of min_range and max_range is used.
        """
        if self.value_type == FlexibleValue.ValueType.SINGLE:
            return self.single_value
        elif self.value_type == FlexibleValue.ValueType.STRING:
            return 0  # Special case is needed to group all strings together in sorting by value
        return (self.max_range + self.min_range) / 2

    def to_dict(self) -> dict:
        """
        Returns a dictionary representing this object, as it's intended to be returned in the API
        """
        return {"value": str(self), "sorting_key": self.sorting_key(), "value_type": self.value_type}

    def __str__(self) -> str:
        if self.value_type == FlexibleValue.ValueType.SINGLE:
            return unit_rule(self.single_value)
        return f"{unit_rule(self.min_range)} - {unit_rule(self.max_range)}"


class WikiDisease(models.Model):
    name = models.CharField(default="", max_length=255, unique=True)
    other_names = models.TextField(default="")
    icd10 = models.CharField(null=True, max_length=64)

    def __str__(self):
        return self.name

    def to_dict(self):
        specialty = self.specialty.all().first()
        frequency = self.frequency
        deaths = self.deaths

        if self.mortality_rate:
            mortality_rate = self.mortality_rate.display_value()
        elif deaths and deaths.frequency_int and frequency and frequency.frequency_int and frequency.frequency_int != 0:
            mortality_rate = deaths.frequency_int / frequency.frequency_int
            mortality_rate = unit_rule(100 * mortality_rate)
        else:
            mortality_rate = "Unknown"

        return {
            "id": self.id,
            "name": self.name,
            "icd10": self.icd10,
            "specialty": specialty.name if specialty else "Unknown",
            "frequency": frequency.display_value() if frequency else "Unknown",
            "deaths": deaths.display_value() if deaths else "Unknown",
            "mortality_rate": mortality_rate,
        }


def unit_rule(val) -> str:
    if val == 0:
        return "0.0000 %"
    if val < 1e-8:
        return f"{round(val*1E9,4)} n%"
    if val < 1e-5:
        return f"{round(val*1E6,4)} µ%"
    if val < 1e-2:
        return f"{round(val*1E3,4)} m%"
    return f"{round(val,4)} %"
