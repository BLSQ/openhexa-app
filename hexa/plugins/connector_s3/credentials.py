from hexa.notebooks.credentials import NotebooksCredentials, NotebooksCredentialsError
from hexa.plugins.connector_s3.api import generate_sts_buckets_credentials
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

        sts_credentials = generate_sts_buckets_credentials(
            user=credentials.user,
            principal_credentials=principal_s3_credentials,
            buckets=buckets,
            duration=60 * 60 * 12,
        )

        credentials.update_env(
            {
                f"AWS_S3_BUCKET_NAMES": ",".join(b.name for b in buckets),
                f"AWS_ACCESS_KEY_ID": sts_credentials["AccessKeyId"],
                f"AWS_SECRET_ACCESS_KEY": sts_credentials["SecretAccessKey"],
                f"AWS_SESSION_TOKEN": sts_credentials["SessionToken"],
            }
        )
        if principal_s3_credentials.default_region != "":
            credentials.update_env(
                {
                    f"AWS_DEFAULT_REGION": principal_s3_credentials.default_region,
                }
            )
