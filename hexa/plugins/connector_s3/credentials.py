from hexa.plugins.connector_s3.models import Credentials, Bucket


def notebooks_credentials(credentials, user):
    """Provide the environment variables that will allow users to access S3 buckets in the notebooks component."""

    try:
        s3_credentials = Credentials.objects.get_for_team(
            user
        )  # TODO: handle multiple teams?
        allowed_buckets = Bucket.objects.filter_for_user(user)
        credentials.update_env(
            {
                "AWS_ACCESS_KEY_ID": s3_credentials.access_key_id,
                "AWS_SECRET_ACCESS_KEY": s3_credentials.secret_access_key,
                "S3_BUCKET_NAMES": ",".join([b.name for b in allowed_buckets]),
            }
        )

    except Credentials.DoesNotExist:
        return {}
