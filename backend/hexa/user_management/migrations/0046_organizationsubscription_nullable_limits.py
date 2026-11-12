from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0045_organization_iframe_webapps_use_play_page"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organizationsubscription",
            name="users_limit",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="organizationsubscription",
            name="workspaces_limit",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="organizationsubscription",
            name="pipeline_runs_limit",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
