from django.db import migrations


def ensure_default_site(apps, schema_editor):
    # AccountMiddleware (allauth) does a Site lookup on every request using SITE_ID=1.
    # django.contrib.sites normally creates this row via post_migrate, but pg-dump
    # restores and some CI setups skip that signal.  This migration guarantees the row
    # exists regardless of how the database was provisioned.
    Site = apps.get_model("sites", "Site")
    Site.objects.get_or_create(
        id=1, defaults={"domain": "example.com", "name": "example.com"}
    )


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0040_organization_slug"),
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [
        migrations.RunPython(ensure_default_site, migrations.RunPython.noop),
    ]
