# Generated by Django 4.1.7 on 2023-06-14 14:54

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("pipelines", "0025_pipeline_container_resources"),
    ]

    operations = [
        migrations.AddField(
            model_name="pipelinerun",
            name="send_mail_notification",
            field=models.BooleanField(default=False, null=True),
        )
    ]