# Generated by Django 4.2.6 on 2023-10-19 12:14

from django.contrib.postgres.operations import CreateCollation
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0008_ci_text"),
    ]

    operations = [
        CreateCollation(
            "case_insensitive",
            provider="icu",
            locale="und-u-ks-level2",
            deterministic=False,
        ),
    ]
