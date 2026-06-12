from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0040_organization_slug"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="aisettings",
            name="ai_settings_enabled_requires_full_config",
        ),
        migrations.AlterField(
            model_name="aisettings",
            name="provider",
            field=models.CharField(
                choices=[
                    ("anthropic", "Anthropic"),
                    ("anthropic_vertex", "Anthropic (Vertex AI)"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="aisettings",
            name="monthly_budget_cents",
            field=models.PositiveIntegerField(
                default=500,
                help_text=(
                    "Per-user monthly spend cap in USD cents (e.g. 500 = $5/month). "
                    "Only enforced for managed providers (e.g. Vertex). Null disables "
                    "the per-user cap."
                ),
                null=True,
            ),
        ),
        migrations.AddConstraint(
            model_name="aisettings",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("enabled", False),
                    models.Q(
                        ("provider", "anthropic_vertex"),
                        ("model__isnull", False),
                    ),
                    models.Q(
                        ("provider__isnull", False),
                        ("model__isnull", False),
                        ("api_key__isnull", False),
                    ),
                    _connector="OR",
                ),
                name="ai_settings_enabled_requires_full_config",
            ),
        ),
    ]
