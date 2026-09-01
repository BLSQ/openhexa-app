from django.db import migrations, models


def set_repository_names(apps, schema_editor):
    """Name the repository of every existing saved query.

    Only the name: the repository itself is created, and the query's first version
    committed, by the `backfill_saved_query_repositories` command. A migration that
    reached out to the git server would fail a deploy wherever that server is not up
    yet, and could not be retried without editing history — while `last_commit` staying
    null here is exactly how the command finds the queries left to do (and how
    `SavedQuery.ensure_repo` heals the ones it misses on their next save).
    """
    SavedQuery = apps.get_model("data_studio", "SavedQuery")
    for saved_query in SavedQuery.objects.select_related("workspace").iterator():
        SavedQuery.objects.filter(pk=saved_query.pk).update(
            repository=f"{saved_query.workspace.slug}-query-{saved_query.pk}"
        )


class Migration(migrations.Migration):
    dependencies = [
        ("data_studio", "0009_alter_querylog_origin"),
    ]

    operations = [
        migrations.AddField(
            model_name="savedquery",
            name="last_commit",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        # Added nullable, filled, then tightened: the column is unique and not null in
        # the end, which no single default could satisfy for rows that already exist.
        migrations.AddField(
            model_name="savedquery",
            name="repository",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.RunPython(set_repository_names, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="savedquery",
            name="repository",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
