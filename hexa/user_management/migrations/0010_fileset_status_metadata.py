# Generated by Django 4.0.4 on 2022-04-25 06:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0009_user_management_to_identity_1"),
    ]

    operations = [
        migrations.AlterField(
            model_name="featureflag",
            name="config",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
