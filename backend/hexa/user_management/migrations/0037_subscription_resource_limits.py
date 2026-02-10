from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0036_serviceaccount"),
    ]

    operations = [
        migrations.AddField(
            model_name="organizationsubscription",
            name="max_pipeline_timeout",
            field=models.PositiveIntegerField(
                null=True,
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="organizationsubscription",
            name="pipeline_cpu_limit",
            field=models.CharField(
                max_length=32,
                blank=True,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="organizationsubscription",
            name="pipeline_memory_limit",
            field=models.CharField(
                max_length=32,
                blank=True,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="organizationsubscription",
            name="notebook_profile",
            field=models.CharField(
                max_length=50,
                blank=True,
                null=True,
            ),
        ),
    ]
