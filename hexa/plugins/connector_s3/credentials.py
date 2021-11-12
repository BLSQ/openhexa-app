import base64
import hashlib
import json

from hexa.notebooks.credentials import NotebooksCredentials, NotebooksCredentialsError
from hexa.plugins.connector_s3.api import generate_sts_user_s3_credentials
from hexa.plugins.connector_s3.models import Bucket, BucketPermissionMode, Credentials


def notebooks_credentials(credentials: NotebooksCredentials):
    """Provides the notebooks credentials data that allows users to access S3 buckets in the notebooks component."""

    ro_buckets = Bucket.objects.filter_by_mode(
        credentials.user, mode=BucketPermissionMode.READ_ONLY
    )
    rw_buckets = Bucket.objects.filter_by_mode(
        credentials.user, mode=BucketPermissionMode.READ_WRITE
    )

    # We only need to generate s3 credentials if the user has access to one or more buckets
    if ro_buckets or rw_buckets:
        try:
            principal_s3_credentials = Credentials.objects.get()
        except (Credentials.DoesNotExist, Credentials.MultipleObjectsReturned):
            raise NotebooksCredentialsError(
                "Your s3 connector plugin should have a single credentials entry"
            )

        session_identifier = credentials.user.email
        if credentials.user.is_superuser:
            role_identifier = "superuser"
        else:
            team_ids = ",".join(
                [str(t.id) for t in credentials.user.team_set.order_by("id")]
            )
            role_identifier = hashlib.blake2s(
                team_ids.encode("utf-8"), digest_size=16
            ).hexdigest()

        sts_credentials = generate_sts_user_s3_credentials(
            principal_credentials=principal_s3_credentials,
            read_only_buckets=ro_buckets,
            read_write_buckets=rw_buckets,
            role_identifier=role_identifier,
            session_identifier=session_identifier,
            duration=60 * 60 * 12,
        )

        credentials.update_env(
            {
                "HEXA_FEATURE_FLAG_S3FS": "false",
                "AWS_S3_BUCKET_NAMES": ",".join(
                    b.name for b in list(ro_buckets) + list(rw_buckets)
                ),
                "AWS_ACCESS_KEY_ID": sts_credentials["AccessKeyId"],
                "AWS_SECRET_ACCESS_KEY": sts_credentials["SecretAccessKey"],
                "AWS_SESSION_TOKEN": sts_credentials["SessionToken"],
            }
        )
        if principal_s3_credentials.default_region != "":
            credentials.update_env(
                {
                    "AWS_DEFAULT_REGION": principal_s3_credentials.default_region,
                }
            )

        if credentials.user.has_feature_flag("s3fs"):
            # use fuse -> _PRIVATE_FUSE_CONFIG used to provide configuration (tokens, buckets)
            fuse_config = {
                "access_key_id": sts_credentials["AccessKeyId"],
                "secret_access_key": sts_credentials["SecretAccessKey"],
                "session_token": sts_credentials["SessionToken"],
                "aws_default_region": principal_s3_credentials.default_region,
                "buckets": [
                    {"name": b.name, "region": str(b.region), "mode": "RO"}
                    for b in ro_buckets
                ]
                + [
                    {"name": b.name, "region": str(b.region), "mode": "RW"}
                    for b in rw_buckets
                ],
            }
            credentials.update_env(
                {
                    "_PRIVATE_FUSE_CONFIG": base64.b64encode(
                        json.dumps(fuse_config).encode()
                    ).decode(),
                    "HEXA_FEATURE_FLAG_S3FS": "true",
                }
            )
