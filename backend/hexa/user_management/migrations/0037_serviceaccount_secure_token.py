from django.db import migrations, models


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
            name="token_prefix",
            field=models.CharField(max_length=8, db_index=True, blank=True, default=""),
        ),
        migrations.AddField(
            model_name="serviceaccount",
            name="token_hash",
            field=models.CharField(max_length=64, unique=True, blank=True, default=""),
        ),
    ]
