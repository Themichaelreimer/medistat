# Generated by Django 4.2 on 2023-04-18 21:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datalake", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="rawdata",
            name="md5_hash",
            field=models.CharField(default="", max_length=32),
            preserve_default=False,
        ),
    ]
