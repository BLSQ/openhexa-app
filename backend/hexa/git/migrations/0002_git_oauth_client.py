from django.db import migrations

LOOPBACK_REDIRECTS = (
    "http://127.0.0.1/ http://127.0.0.1 http://localhost/ http://localhost"
)

GITEA_OAUTH_CLIENT_ID = "e90ee53c-94e2-48ac-9358-a874fb9e0662"
OPENHEXA_GIT_CLIENT_ID = "openhexa-git"

CLIENTS = [
    {"client_id": GITEA_OAUTH_CLIENT_ID, "name": "OpenHEXA Git (Gitea-compatible)"},
    {"client_id": OPENHEXA_GIT_CLIENT_ID, "name": "OpenHEXA Git"},
]


def create_git_oauth_clients(apps, schema_editor):
    Application = apps.get_model("oauth2_provider", "Application")
    for client in CLIENTS:
        Application.objects.update_or_create(
            client_id=client["client_id"],
            defaults={
                "name": client["name"],
                "client_type": "public",
                "authorization_grant_type": "authorization-code",
                "client_secret": "",
                "hash_client_secret": False,
                "redirect_uris": LOOPBACK_REDIRECTS,
                "skip_authorization": False,
                "algorithm": "",
            },
        )


def remove_git_oauth_clients(apps, schema_editor):
    Application = apps.get_model("oauth2_provider", "Application")
    Application.objects.filter(client_id__in=[c["client_id"] for c in CLIENTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("git", "0001_initial"),
        (
            "oauth2_provider",
            "0013_alter_application_authorization_grant_type_device",
        ),
    ]

    operations = [
        migrations.RunPython(create_git_oauth_clients, remove_git_oauth_clients),
    ]
