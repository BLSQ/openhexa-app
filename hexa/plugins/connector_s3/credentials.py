from hexa.notebooks.credentials import NotebooksCredentials
from hexa.plugins.connector_s3.api import generate_sts_buckets_credentials
from hexa.plugins.connector_s3.models import Bucket
from hexa.user_management.models import User


def notebooks_credentials(notebook_credentials: NotebooksCredentials, user: User):
    """Provides the notebooks credentials data that allows users to access S3 buckets in the notebooks component."""

    notebook_credentials_data = {}
    allowed_buckets = Bucket.objects.filter_for_user(user)

    # The first step is to distinguish between:
    # - buckets that will be accessed using AWS STS temporary credentials (the recommended approach)
    # - buckets that will be access through the credentials attached to the bucket (when we can't use STS)
    sts_credentials_buckets = [
        b for b in allowed_buckets if b.api_credentials.role_arn != ""
    ]
    api_credentials_buckets = [
        b for b in allowed_buckets if b.api_credentials.role_arn == ""
    ]

    # For STS credentials, the first step is to group the buckets by "principal credentials"
    sts_credentials = {}
    for bucket in sts_credentials_buckets:
        if (
            bucket.api_credentials.username not in sts_credentials
        ):  # STS temporary credentials
            sts_credentials[bucket.api_credentials.username] = {
                "principal_credentials": bucket.api_credentials,
                "buckets": [],
            }

        sts_credentials[bucket.api_credentials.username]["buckets"].append(bucket)

    # Now that we now which principal credentials to use for a set of buckets, we can generate the STS credentials
    for principal_username in sts_credentials:
        sts_credentials[principal_username][
            "sts_credentials"
        ] = generate_sts_buckets_credentials(
            user=user,
            principal_credentials=sts_credentials[principal_username][
                "principal_credentials"
            ],
            buckets=sts_credentials[principal_username]["buckets"],
        )

    # Now that we have all credentials (STS and API credentials), we can build the credentials data itself
    for bucket in api_credentials_buckets:
        notebook_credentials_data[bucket.s3_name] = {
            "AWS_ACCESS_KEY_ID": bucket.api_credentials.access_key_id,
            "AWS_SECRET_ACCESS_KEY": bucket.api_credentials.secret_access_key,
        }
    for principal_username, credentials_data in sts_credentials.items():
        for bucket in credentials_data["buckets"]:
            notebook_credentials_data[bucket.s3_name] = {
                "AWS_ACCESS_KEY_ID": credentials_data["sts_credentials"]["AccessKeyId"],
                "AWS_SECRET_ACCESS_KEY": credentials_data["sts_credentials"][
                    "SecretAccessKey"
                ],
                "AWS_SESSION_TOKEN": credentials_data["sts_credentials"][
                    "SessionToken"
                ],
            }

    notebook_credentials.update_data(notebook_credentials_data)
