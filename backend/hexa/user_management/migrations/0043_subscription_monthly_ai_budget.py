from django.db import migrations, models

PLAN_BUDGETS = {
    "oh_trial": 10,
    "oh_starter": 50,
    "oh_growth": 100,
    "oh_scale": 250,
}
DEFAULT_BUDGET = 10  # just in case there's an unknown plan
BLSQ_BUDGET = 500  # exception for the BLSQ org


def set_monthly_ai_budget(apps, schema_editor):
    OrganizationSubscription = apps.get_model(
        "user_management", "OrganizationSubscription"
    )
    for subscription in OrganizationSubscription.objects.select_related("organization"):
        if subscription.organization.short_name == "BLSQ":
            subscription.monthly_ai_budget = BLSQ_BUDGET
        else:
            subscription.monthly_ai_budget = PLAN_BUDGETS.get(
                subscription.plan_code, DEFAULT_BUDGET
            )
        subscription.save(update_fields=["monthly_ai_budget"])


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0042_aisettings_organization"),
    ]

    operations = [
        migrations.AddField(
            model_name="organizationsubscription",
            name="monthly_ai_budget",
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.RunPython(
            set_monthly_ai_budget,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="organizationsubscription",
            name="monthly_ai_budget",
            field=models.PositiveIntegerField(),
        ),
    ]
