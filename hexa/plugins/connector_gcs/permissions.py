from hexa.plugins.connector_gcs.models import Bucket, GCSBucketPermission
from hexa.user_management.models import PermissionMode, User


def write(principal: User, bucket: Bucket):
    if not principal.is_authenticated:
        return False
    elif principal.is_superuser:
        return True
    elif (
        GCSBucketPermission.objects.filter(
            bucket=bucket,
            team_id__in=principal.team_set.all().values("id"),
            mode__in=[PermissionMode.EDITOR, PermissionMode.OWNER],
        ).count()
        > 0
    ):
        return True
    else:
        return False
