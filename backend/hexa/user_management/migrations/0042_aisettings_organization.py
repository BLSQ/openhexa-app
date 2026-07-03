import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import hexa.core.models.cryptography


def create_default_ai_settings(apps, schema_editor):
    Organization = apps.get_model("user_management", "Organization")
    AiSettings = apps.get_model("user_management", "AiSettings")
    # Managed (hosted) instances default to the assistant being on with our hosted
    # provider; self-hosted instances start disabled until an admin configures their
    # own provider and API key.
    managed = settings.ASSISTANT_MANAGED
    AiSettings.objects.bulk_create(
        [
            AiSettings(
                organization=organization,
                enabled=managed,
                provider="managed" if managed else "anthropic",
            )
            for organization in Organization.objects.all()
        ]
    )


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0041_ensure_default_site"),
    ]

    operations = [
        # Existing per-user configurations are intentionally discarded: AiSettings
        # is re-keyed on Organization and every organization gets a fresh default.
        migrations.DeleteModel(
            name="AiSettings",
        ),
        migrations.CreateModel(
            name="AiSettings",
            fields=[
                (
                    "organization",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="ai_settings",
                        serialize=False,
                        to="user_management.organization",
                    ),
                ),
                ("enabled", models.BooleanField(default=False)),
                (
                    "provider",
                    models.CharField(
                        choices=[
                            ("managed", "Managed"),
                            ("anthropic", "Anthropic"),
                        ],
                        default="anthropic",
                        max_length=20,
                    ),
                ),
                (
                    "model",
                    models.CharField(
                        choices=[
                            ("haiku", "Claude Haiku 4.5"),
                            ("opus", "Claude Opus 4.6"),
                            ("sonnet", "Claude Sonnet 4.6"),
                        ],
                        max_length=30,
                        null=True,
                    ),
                ),
                (
                    "api_key",
                    hexa.core.models.cryptography.EncryptedTextField(
                        max_length=255, null=True
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(
                            ("enabled", False),
                            ("provider", "managed"),
                            models.Q(
                                ("model__isnull", False),
                                ("api_key__isnull", False),
                            ),
                            _connector="OR",
                        ),
                        name="ai_settings_enabled_requires_full_config",
                    )
                ],
            },
        ),
        migrations.RunPython(create_default_ai_settings, migrations.RunPython.noop),
    ]
