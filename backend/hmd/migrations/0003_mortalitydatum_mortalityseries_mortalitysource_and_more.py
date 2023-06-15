# Generated by Django 4.2 on 2023-04-10 03:05

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("hmd", "0002_auto_20210309_0427"),
    ]

    operations = [
        migrations.CreateModel(
            name="MortalityDatum",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("value", models.DecimalField(decimal_places=6, max_digits=12)),
            ],
        ),
        migrations.CreateModel(
            name="MortalitySeries",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sex",
                    models.CharField(
                        choices=[("m", "m"), ("f", "f"), ("a", "a")],
                        default="a",
                        max_length=1,
                    ),
                ),
                ("age", models.IntegerField()),
                (
                    "tags",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.IntegerField(),
                        size=None,
                        verbose_name="choices",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MortalitySource",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                ("link", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="MortalityTag",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=64)),
            ],
        ),
        migrations.RemoveField(
            model_name="countryagepopulation",
            name="country",
        ),
        migrations.RemoveField(
            model_name="countrybirths",
            name="country",
        ),
        migrations.DeleteModel(
            name="CountryAgeDeaths",
        ),
        migrations.DeleteModel(
            name="CountryAgePopulation",
        ),
        migrations.DeleteModel(
            name="CountryBirths",
        ),
        migrations.AddIndex(
            model_name="mortalitytag",
            index=models.Index(fields=["name"], name="hmd_mortali_name_df5799_idx"),
        ),
        migrations.AddIndex(
            model_name="mortalitysource",
            index=models.Index(fields=["name"], name="hmd_mortali_name_21e077_idx"),
        ),
        migrations.AddField(
            model_name="mortalityseries",
            name="country",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="hmd.country",
            ),
        ),
        migrations.AddField(
            model_name="mortalityseries",
            name="source",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="hmd.mortalitysource"),
        ),
        migrations.AddField(
            model_name="mortalitydatum",
            name="series",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="hmd.mortalityseries"),
        ),
        migrations.AddIndex(
            model_name="mortalityseries",
            index=models.Index(
                fields=["tags", "country", "sex", "age"],
                name="hmd_mortali_tags_45e22b_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="mortalitydatum",
            index=models.Index(fields=["series", "-date"], name="hmd_mortali_series__bf1fb1_idx"),
        ),
    ]
