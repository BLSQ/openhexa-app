# Generated by Django 4.0.4 on 2022-05-17 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("connector_accessmod", "0042_am_roles_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="fileset",
            name="mode",
            field=models.CharField(
                choices=[
                    ("USER_INPUT", "User Input"),
                    ("AUTOMATIC_ACQUISITION", "Automatic Acquisition"),
                ],
                default="USER_INPUT",
                max_length=50,
            ),
        ),
    ]