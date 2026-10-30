from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mcp", "0002_mcp_connection"),
        ("user_management", "0045_organization_iframe_webapps_use_play_page"),
    ]

    operations = [
        migrations.AddField(
            model_name="mcpconnection",
            name="organizations",
            field=models.ManyToManyField(
                blank=True,
                related_name="mcp_connections",
                to="user_management.organization",
            ),
        ),
    ]
