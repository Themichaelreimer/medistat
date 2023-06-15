# Generated by Django 4.2 on 2023-04-18 21:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datalake", "0002_rawdata_md5_hash"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="rawdata",
            index=models.Index(fields=["source", "md5_hash"], name="datalake_ra_source__13a82d_idx"),
        ),
    ]
