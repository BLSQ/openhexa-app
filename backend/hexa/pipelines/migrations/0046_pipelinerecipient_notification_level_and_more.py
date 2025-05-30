# Generated by Django 5.0.9 on 2024-11-12 08:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pipelines", "0045_alter_pipelinerun_duration_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="pipelinerecipient",
            name="notification_level",
            field=models.CharField(
                choices=[("ALL", "All"), ("ERROR", "Error")],
                default="ALL",
                max_length=200,
            ),
        ),
        migrations.AlterField(
            model_name="pipelinerun",
            name="send_mail_notifications",
            field=models.BooleanField(default=True),
        ),
    ]
