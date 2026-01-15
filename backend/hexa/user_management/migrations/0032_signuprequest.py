import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0031_organization_deleted_at_organization_logo_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="SignupRequest",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "email",
                    models.EmailField(db_collation="case_insensitive", max_length=254),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("PENDING", "Pending"), ("ACCEPTED", "Accepted")],
                        default="PENDING",
                        max_length=50,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
