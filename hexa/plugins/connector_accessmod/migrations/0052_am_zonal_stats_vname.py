# Generated by Django 4.0.4 on 2022-07-01 12:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("connector_accessmod", "0051_am_acc_default_algo"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="zonalstatisticsanalysis",
            options={"verbose_name_plural": "Zonal stats analyses"},
        ),
    ]