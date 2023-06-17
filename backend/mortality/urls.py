"""mortality URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

import wiki.views as wiki_views
import hmd.views as hmd_views
import accounts.views as accounts_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", accounts_views.user_login),
    path("accounts/logout/", accounts_views.user_logout),
    # Old version of api
    path("diseases/", wiki_views.disease_index),
    path("lifetables/", hmd_views.get_life_table),
    path("lifetable_years/", hmd_views.get_lifetable_years),
    path("lifetables_countries/", hmd_views.get_countries),
    # New version of api
    path("hmd/series_index/", hmd_views.series_index),
    path("hmd/series_data/", hmd_views.get_series_data),
]
