import string

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.conf import settings
from hmd.models import Country, LifeTable, MortalityDatum, MortalitySeries, MortalityTag


def add_access_control_headers(resp: JsonResponse) -> JsonResponse:
    response = resp
    if settings.DEBUG:
        response["Access-Control-Allow-Origin"] = "*"
    else:
        response["Access-Control-Allow-Origin"] = "medistat.online"
    response["Access-Control-Allow-Methods"] = "POST"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response


@csrf_exempt
def get_countries(request: HttpRequest) -> JsonResponse:
    key = "countries"
    if result := cache.get(key):
        return result

    countries = Country.objects.all().values("id", "name").order_by("name")
    data = list(countries)

    result = add_access_control_headers(JsonResponse(data, safe=False))
    cache.set(key, result)
    return result


@csrf_exempt
def get_lifetable_years(request: HttpRequest) -> JsonResponse:
    country = request.POST.get("country")
    cache_key = f"lifetable_country_years"

    if result := cache.get(cache_key):
        return result

    years = [x["year"] for x in LifeTable.objects.filter(country__name=country).values("year").distinct().order_by("-year")]

    result = add_access_control_headers(JsonResponse(years, safe=False))
    cache.set(cache_key, result)
    return result


@csrf_exempt
def get_life_table(request: HttpRequest) -> JsonResponse:
    country = request.POST.get("country")
    sex = request.POST.get("sex", "").lower()[0]
    year = request.POST.get("year")
    cache_key = f"{country}{year}{sex}".lower()
    cache_key = "".join([c for c in cache_key if c in string.ascii_lowercase or c in string.digits])

    if result := cache.get(cache_key):
        return result

    life_table = (
        LifeTable.objects.filter(country__name=country, year=year, sex=sex, age__lte=109)
        .order_by("age")
        .values("age", "probability", "cumulative_probability")
    )
    life_table = list(life_table)

    result = add_access_control_headers(JsonResponse(life_table, safe=False))
    cache.set(cache_key, result)
    return result


@csrf_exempt
def series_index(request: HttpRequest) -> JsonResponse:
    cache_key = "series_index"
    if result := cache.get(cache_key):
        return result

    result = [x for x in MortalitySeries.objects.order_by("id").values("id", "tags")]
    for r in result:
        r["tags"] = [x[0] for x in MortalityTag.objects.filter(id__in=r["tags"]).values_list("name")]

    result = add_access_control_headers(JsonResponse(result, safe=False))
    cache.set(cache_key, result)
    return result


@csrf_exempt
def get_series_data(request: HttpRequest) -> JsonResponse:
    pass
