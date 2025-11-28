import secrets

from django.core.validators import validate_slug
from django.db import migrations, models
from django.db.models import Q
from slugify import slugify


def generate_slugs_for_existing_webapps(apps, schema_editor):
    """Generate slugs for all existing webapps."""
    Webapp = apps.get_model("webapps", "Webapp")

    for webapp in Webapp.objects.all():
        workspace_id = webapp.workspace_id
        base_name = webapp.name

        suffix = ""
        while True:
            base_slug = slugify(base_name)[:40].rstrip("-")
            slug = base_slug + suffix

            if not Webapp.objects.filter(workspace_id=workspace_id, slug=slug).exists():
                webapp.slug = slug
                webapp.save(update_fields=["slug"])
                break

            suffix = "-" + secrets.token_hex(3)


class Migration(migrations.Migration):
    dependencies = [
        ("webapps", "0003_remove_feature_flag"),
    ]

    operations = [
        migrations.AddField(
            model_name="webapp",
            name="slug",
            field=models.CharField(
                default="temp",
                editable=False,
                max_length=100,
                validators=[validate_slug],
            ),
            preserve_default=False,
        ),
        migrations.RunPython(
            generate_slugs_for_existing_webapps, reverse_code=migrations.RunPython.noop
        ),
        migrations.AddConstraint(
            model_name="webapp",
            constraint=models.UniqueConstraint(
                condition=Q(deleted_at__isnull=True),
                fields=("workspace_id", "slug"),
                name="unique_webapp_slug_per_workspace",
            ),
        ),
    ]
