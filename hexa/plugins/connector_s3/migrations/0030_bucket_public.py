# Generated by Django 4.0.4 on 2022-04-27 19:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("connector_s3", "0029_permissions_next"),
    ]

    operations = [
        migrations.AddField(
            model_name="bucket",
            name="public",
            field=models.BooleanField(default=False),
        ),
    ]
