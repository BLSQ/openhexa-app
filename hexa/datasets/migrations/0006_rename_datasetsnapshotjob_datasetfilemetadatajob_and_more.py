# Generated by Django 5.0.3 on 2024-07-12 07:44

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("datasets", "0005_datasetsnapshotjob"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="DatasetSnapshotJob",
            new_name="DatasetFileMetadataJob",
        ),
        migrations.AlterModelTable(
            name="datasetfilemetadatajob",
            table="datasets_filemetadatajob",
        ),
    ]