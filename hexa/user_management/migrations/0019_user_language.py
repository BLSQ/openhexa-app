# Generated by Django 4.1.7 on 2024-01-03 10:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0018_remove_user_accepted_tos"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="language",
            field=models.CharField(default="en", max_length=10),
        ),
    ]
