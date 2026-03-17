import secrets

from django.db import migrations, models
from slugify import slugify


def create_organization_slug(name, Organization, max_attempts=10):
    suffix = ""
    for _ in range(max_attempts):
        slug = slugify(name[: 200 - len(suffix)] + suffix)
        if not Organization.objects.filter(slug=slug).exists():
            return slug
        suffix = "-" + secrets.token_hex(3)
    raise ValueError(f"Could not generate a unique slug for organization '{name}'")


def populate_slugs(apps, schema_editor):
    Organization = apps.get_model("user_management", "Organization")
    for org in Organization.objects.all():
        org.slug = create_organization_slug(org.name, Organization)
        org.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0039_aisettings"),
    ]

    operations = [
        migrations.AddField(
            model_name="organization",
            name="slug",
            field=models.CharField(max_length=200, default="", editable=False),
            preserve_default=False,
        ),
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="organization",
            name="slug",
            field=models.CharField(max_length=200, unique=True, editable=False),
        ),
    ]
