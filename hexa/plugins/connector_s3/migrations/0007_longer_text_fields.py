# Generated by Django 3.2.3 on 2021-06-11 12:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("connector_s3", "0006_s3_credentials_simplification"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bucket",
            name="name",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="bucket",
            name="short_name",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="object",
            name="name",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="object",
            name="short_name",
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
