# Generated by Django 3.2.6 on 2021-08-10 08:40

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0001_initial"),
        ("connector_s3", "0017_remove_parent_add_dirname"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="bucketpermission",
            unique_together={("bucket", "team")},
        ),
    ]
