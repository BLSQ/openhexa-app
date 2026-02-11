import hashlib
import secrets

from django.db import migrations, models


def generate_tokens_for_existing_accounts(apps, schema_editor):
    ServiceAccount = apps.get_model("user_management", "ServiceAccount")
    for svc in ServiceAccount.objects.all():
        raw_token = secrets.token_urlsafe(32)
        svc.token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        svc.save(update_fields=["token_hash"])


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0036_serviceaccount"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="serviceaccount",
            name="access_token",
        ),
        migrations.AddField(
            model_name="serviceaccount",
            name="token_hash",
            field=models.CharField(max_length=64, blank=True, default=""),
        ),
        migrations.RunPython(
            generate_tokens_for_existing_accounts,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="serviceaccount",
            name="token_hash",
            field=models.CharField(max_length=64, unique=True, blank=True, default=""),
        ),
    ]
