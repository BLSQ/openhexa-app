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
    ]
