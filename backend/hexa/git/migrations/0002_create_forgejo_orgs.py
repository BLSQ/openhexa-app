import logging

from django.db import migrations

logger = logging.getLogger(__name__)


def create_forgejo_orgs(apps, schema_editor):
    Organization = apps.get_model("user_management", "Organization")

    try:
        from hexa.git.forgejo import get_forgejo_client

        client = get_forgejo_client()
    except Exception:
        logger.warning("Could not connect to Forgejo, skipping org creation")
        return

    for org in Organization.objects.all():
        client.create_organization(org.slug, org.name)


class Migration(migrations.Migration):
    dependencies = [
        ("git", "0001_initial"),
        ("user_management", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_forgejo_orgs, migrations.RunPython.noop),
    ]
