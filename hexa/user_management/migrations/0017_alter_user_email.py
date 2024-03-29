# Generated by Django 4.2.6 on 2023-10-19 12:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0016_auto_20230330_1506"),
        ("core", "0009_case_insensitive_collation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                db_collation="case_insensitive",
                max_length=254,
                unique=True,
                verbose_name="email address",
            ),
        ),
    ]
