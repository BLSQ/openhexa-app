from django.db import migrations

import hexa.user_management.models


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0040_organization_slug"),
        ("workspaces", "0062_merge_20260804_0809"),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkspaceTokenUser",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=(
                "user_management.user",
                hexa.user_management.models.WorkspaceScopedPrincipal,
            ),
            managers=[
                ("objects", hexa.user_management.models.UserManager()),
            ],
        ),
    ]
