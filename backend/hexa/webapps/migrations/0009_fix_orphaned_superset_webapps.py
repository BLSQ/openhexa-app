from django.db import migrations


def fix_orphaned_superset_webapps(apps, schema_editor):
    Webapp = apps.get_model("webapps", "Webapp")
    SupersetWebapp = apps.get_model("webapps", "SupersetWebapp")

    superset_webapp_ids = SupersetWebapp.objects.filter(
        superset_dashboard__isnull=False
    ).values_list("webapp_ptr_id", flat=True)
    Webapp.objects.filter(type="superset").exclude(pk__in=superset_webapp_ids).update(
        type="iframe"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("webapps", "0008_webapp_is_public"),
    ]

    operations = [
        migrations.RunPython(fix_orphaned_superset_webapps, migrations.RunPython.noop),
    ]
