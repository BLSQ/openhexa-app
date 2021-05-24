import stringcase
import typing

from hexa.notebooks.credentials import NotebooksCredentials
from hexa.plugins.connector_s3.api import generate_sts_buckets_credentials
from hexa.plugins.connector_s3.models import Bucket


def notebooks_credentials(credentials: NotebooksCredentials):
    """Provides the notebooks credentials data that allows users to access S3 buckets in the notebooks component."""

    buckets = Bucket.objects.filter_for_user(credentials.user)

    # STS temporary credentials (preferred approach)
    _sts_bucket_credentials(
        credentials, [b for b in buckets if b.api_credentials.use_sts_credentials]
    )

    # API credentials (when we can't use STS)
    _api_bucket_credentials(
        credentials, [b for b in buckets if not b.api_credentials.use_sts_credentials]
    )


def _api_bucket_credentials(
    credentials: NotebooksCredentials, buckets: typing.Sequence[Bucket]
):
    """Build credentials env variables for "API credentials" buckets"""

    env = {}
    for bucket in buckets:
        env_key = _bucket_env_key(bucket.s3_name)
        env.update(
            {
                f"{env_key}_BUCKET_NAME": bucket.s3_name,
                f"{env_key}_ACCESS_KEY_ID": bucket.api_credentials.access_key_id.decrypt(),
                f"{env_key}_SECRET_ACCESS_KEY": bucket.api_credentials.secret_access_key.decrypt(),
            }
        )

    credentials.update_env(env)


def _sts_bucket_credentials(
    credentials: NotebooksCredentials, buckets: typing.Sequence[Bucket]
):
    """Build credentials env variables for "STS credentials" buckets"""

    # The first step is to group the buckets by "principal credentials"
    buckets_by_credentials = {}
    for bucket in buckets:
        if bucket.api_credentials not in buckets_by_credentials:
            buckets_by_credentials[bucket.api_credentials] = []

        buckets_by_credentials[bucket.api_credentials].append(bucket)

    # Now that we now which principal credentials to use for a set of buckets, we can generate the STS credentials
    env = {}
    for api_credentials, buckets in buckets_by_credentials:
        sts_credentials = generate_sts_buckets_credentials(
            user=credentials.user,
            principal_credentials=api_credentials,
            buckets=buckets,
        )

        for bucket in buckets:
            env_key = _bucket_env_key(bucket.s3_name)
            env.update(
                {
                    f"{env_key}_BUCKET_NAME": bucket.s3_name,
                    f"{env_key}_ACCESS_KEY_ID": sts_credentials["AccessKeyId"],
                    f"{env_key}_SECRET_ACCESS_KEY": sts_credentials["SecretAccessKey"],
                    f"{env_key}_SESSION_TOKEN": sts_credentials["SessionToken"],
                }
            )

    credentials.update_env(env)


def _bucket_env_key(bucket_name: str) -> str:
    """Generates a nice prefix for bucket environment variables"""

    return f"S3_{stringcase.snakecase(bucket_name).upper()}"
