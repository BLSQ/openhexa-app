from django.db import migrations, models


def set_repository_names(apps, schema_editor):
    """Name the repository of every existing saved query, without creating any.

    Creating them is the `backfill_saved_query_repositories` command's job: a migration
    reaching the git server would fail a deploy wherever it is not up yet. `last_commit`
    staying null is how that command finds the queries left to do.
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
        # Added nullable, filled, then tightened: the column ends up unique and not
        # null, which no single default could satisfy for existing rows.
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
