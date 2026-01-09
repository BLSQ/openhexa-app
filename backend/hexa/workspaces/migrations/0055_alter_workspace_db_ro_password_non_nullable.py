from django.db import migrations

import hexa.core.models.cryptography


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0054_create_readonly_roles"),
    ]

    operations = [
        migrations.AlterField(
            model_name="workspace",
            name="db_ro_password",
            field=hexa.core.models.cryptography.EncryptedTextField(),
        ),
    ]
