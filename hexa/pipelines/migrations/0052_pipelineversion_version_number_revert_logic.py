from django.db import migrations
from django.db.models import F, Value
from django.db.models.functions import Concat


def fill_empty_names(apps, _):
    PipelineVersion = apps.get_model("pipelines", "PipelineVersion")
    PipelineVersion.objects.filter(name__isnull=True).update(
        name=Concat(Value("v"), F("version_number"), Value(" (auto-generated name)"))
    )


class Migration(migrations.Migration):
    dependencies = [("pipelines", "0051_pipelineversion_version_number_cleanup")]

    operations = [
        migrations.RunPython(migrations.RunPython.noop, reverse_code=fill_empty_names),
    ]
