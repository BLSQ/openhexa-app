from django.db import migrations, models


def migrate_html_bundle_to_static(apps, schema_editor):
    Webapp = apps.get_model("webapps", "Webapp")
    Webapp.objects.filter(type__in=["html", "bundle"]).update(type="static")


class Migration(migrations.Migration):
    dependencies = [
        ("webapps", "0009_gitwebapp_alter_webapp_url"),
    ]

    operations = [
        migrations.RunPython(migrate_html_bundle_to_static, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="webapp",
            name="type",
            field=models.CharField(
                choices=[
                    ("iframe", "iFrame"),
                    ("static", "Static"),
                    ("superset", "Superset"),
                ],
                default="iframe",
                max_length=20,
            ),
        ),
    ]
