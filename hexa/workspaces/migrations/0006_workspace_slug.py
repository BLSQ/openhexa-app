# Generated by Django 4.1.3 on 2023-02-06 11:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0005_workspace_members_alter_workspace_created_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="workspace",
            name="slug",
            field=models.CharField(max_length=30, null=True),
        ),
    ]
