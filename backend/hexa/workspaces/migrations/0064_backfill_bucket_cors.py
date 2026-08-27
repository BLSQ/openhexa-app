from django.db import migrations

from hexa.files import storage
from hexa.files.backends.base import SupportsBucketCors


def backfill_bucket_cors(apps, schema_editor):
    """Re-apply the storage backend CORS policy to every existing workspace bucket.

    The policy was only ever written by create_bucket, so buckets created before
    the wildcard policy landed (commit 1362f0dc, July 2024) kept the original
    one, restricted to app.openhexa.org / accessmod.openhexa.org and to
    GET + PUT. Browser uploads and downloads from any other origin fail their
    preflight on those buckets.
    """
    if not isinstance(storage, SupportsBucketCors):
        return

    Workspace = apps.get_model("workspaces", "Workspace")
    bucket_names = list(
        Workspace.objects.exclude(bucket_name__isnull=True)
        .exclude(bucket_name="")
        .values_list("bucket_name", flat=True)
    )
    if not bucket_names:
        return

    failed = []
    for bucket_name in bucket_names:
        try:
            storage.set_bucket_cors(bucket_name)
        except Exception as exc:
            failed.append(bucket_name)
            print(f"[0064] Skipping {bucket_name}: {exc}")

    if len(failed) == len(bucket_names):
        raise RuntimeError(
            f"[0064] CORS backfill failed for all {len(bucket_names)} buckets. "
            "Check the storage credentials and that the role is allowed to "
            "update bucket configuration."
        )


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("workspaces", "0063_workspace_tags"),
    ]

    operations = [
        migrations.RunPython(
            backfill_bucket_cors,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
