# Generated by Django 4.0.6 on 2022-07-28 11:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data_collections", "0001_data_collections"),
        ("connector_dhis2", "0028_instance_public"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataElementCollectionEntry",
            fields=[
                (
                    "collectionentry_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="data_collections.collectionentry",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("data_collections.collectionentry",),
        ),
        migrations.AddField(
            model_name="dataelement",
            name="collections",
            field=models.ManyToManyField(
                related_name="+",
                through="connector_dhis2.DataElementCollectionEntry",
                to="data_collections.collection",
            ),
        ),
        migrations.AddField(
            model_name="dataelementcollectionentry",
            name="data_element",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="connector_dhis2.dataelement",
            ),
        ),
    ]