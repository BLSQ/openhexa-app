from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pipeline_templates", "0012_pipelinetemplate_validated_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pipelinetemplate",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="pipelinetemplateversion",
            name="name",
            field=models.CharField(blank=True, max_length=250, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="pipelinetemplateversion",
            name="documentation",
            field=models.TextField(blank=True, null=True),
        ),
    ]
