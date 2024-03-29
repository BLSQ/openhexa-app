# Generated by Django 4.1.7 on 2023-08-11 12:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0033_alter_connectionfield_options"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="workspaceinvitation",
            constraint=models.UniqueConstraint(
                models.F("email"),
                models.F("workspace"),
                name="workspace_invitation_unique_workspace_email",
            ),
        ),
    ]
