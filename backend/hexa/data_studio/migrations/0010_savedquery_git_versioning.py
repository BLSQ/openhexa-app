from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data_studio", "0009_alter_querylog_origin"),
    ]

    operations = [
        # Nullable on purpose, and left null for every existing query: creating the
        # repositories is the `backfill_saved_query_repositories` command's job, since
        # a migration reaching the git server would fail a deploy wherever it is not up
        # yet. Null is how that command finds the queries left to do.
        migrations.AddField(
            model_name="savedquery",
            name="repository",
            field=models.CharField(max_length=255, null=True, unique=True),
        ),
        # Deletion becomes soft, so that a deleted query keeps the slug its repository
        # is named after (see `generate_saved_query_slug`).
        migrations.AddField(
            model_name="savedquery",
            name="deleted_at",
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="savedquery",
            name="restored_at",
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.RemoveConstraint(
            model_name="savedquery",
            name="data_studio_private_query_has_author",
        ),
        migrations.AddConstraint(
            model_name="savedquery",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("created_by__isnull", False),
                    models.Q(("visibility", "PRIVATE"), _negated=True),
                    ("deleted_at__isnull", False),
                    _connector="OR",
                ),
                name="data_studio_private_query_has_author",
            ),
        ),
    ]
