from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0040_organization_slug"),
        ("webapps", "0019_webappuser"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="WebappUser",
            new_name="PrivateWebappUser",
        ),
    ]
