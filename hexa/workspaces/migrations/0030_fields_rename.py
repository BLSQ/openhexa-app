# Generated by Django 4.1.7 on 2023-04-24 13:39

from django.db import migrations

from hexa.workspaces.models import ConnectionType


def rename_fields(apps, schema_editor):
    ConnectionField = apps.get_model("workspaces", "ConnectionField")
    for field in ConnectionField.objects.all():
        if (
            field.connection.connection_type == ConnectionType.POSTGRESQL
            and field.code == "database"
        ):
            field.code = "db_name"
            field.save()
        elif (
            field.connection.connection_type == ConnectionType.DHIS2
            and field.code == "api_url"
        ):
            field.code = "url"
            field.save()


def undo_rename_fields(apps, schema_editor):
    ConnectionField = apps.get_model("workspaces", "ConnectionField")
    for field in ConnectionField.objects.all():
        if (
            field.connection.connection_type == ConnectionType.POSTGRESQL
            and field.code == "db_name"
        ):
            field.code = "database"
            field.save()
        elif (
            field.connection.connection_type == ConnectionType.DHIS2
            and field.code == "url"
        ):
            field.code = "api_url"
            field.save()


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0029_merge_20230418_0956"),
    ]

    operations = [
        migrations.RunPython(rename_fields, reverse_code=undo_rename_fields),
    ]