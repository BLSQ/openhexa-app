from django.db import migrations

import hexa.core.models.cryptography


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0052_workspace_archived_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="workspace",
            name="db_ro_password",
            field=hexa.core.models.cryptography.EncryptedTextField(
                blank=True, null=True
            ),
        ),
    ]
