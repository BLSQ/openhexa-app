# Generated by Django 4.0.6 on 2022-09-05 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data_collections", "0001_collections"),
    ]

    operations = [
        migrations.AddField(
            model_name="collection",
            name="summary",
            field=models.TextField(blank=True, null=True),
        ),
    ]