# Generated by Django 4.1.7 on 2023-09-13 10:28

from django.db import migrations


def update_gcs_connections_service_account_key(apps, schema_editor):
    Connection = apps.get_model("workspaces", "Connection")
    ConnectionField = apps.get_model("workspaces", "ConnectionField")

    gcs_connections = Connection.objects.filter(connection_type="GCS")
    service_account_fields = []
    for conn in gcs_connections:
        service_account_field = conn.fields.filter(code="service_account_key").first()
        service_account_field.secret = True
        service_account_fields.append(service_account_field)

    ConnectionField.objects.bulk_update(service_account_fields, ["secret"])


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0035_workspace_datasets"),
    ]

    operations = [
        migrations.RunPython(update_gcs_connections_service_account_key),
    ]
