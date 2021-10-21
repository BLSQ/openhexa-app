import hashlib

from hexa.notebooks.credentials import NotebooksCredentials, NotebooksCredentialsError
from hexa.plugins.connector_s3.api import generate_sts_user_s3_credentials
from hexa.plugins.connector_s3.models import Bucket, Credentials


def notebooks_credentials(credentials: NotebooksCredentials):
    """Provides the notebooks credentials data that allows users to access S3 buckets in the notebooks component."""

    buckets = Bucket.objects.filter_for_user(credentials.user)

    # We only need to generate s3 credentials if the user has access to one or more buckets
    if len(buckets) > 0:
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
            buckets=buckets,
            role_identifier=role_identifier,
            session_identifier=session_identifier,
            duration=60 * 60 * 12,
        )

        credentials.update_env(
            {
                "HEXA_FEATURE_FLAG_S3FS": "true"
                if credentials.user.has_feature_flag("s3fs")
                else "false",
                "AWS_S3_BUCKET_NAMES": ",".join(b.name for b in buckets),
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
