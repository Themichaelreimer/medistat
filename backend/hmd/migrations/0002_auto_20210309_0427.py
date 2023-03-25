# Generated by Django 3.0.8 on 2021-03-09 04:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hmd", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="lifetable",
            name="year",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="country",
            name="short_name",
            field=models.CharField(max_length=8),
        ),
    ]
