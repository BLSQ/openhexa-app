from hexa.plugins.connector_s3.models import Bucket, BucketPermission
from hexa.user_management.models import PermissionMode, User


def write(principal: User, bucket: Bucket):
    if not principal.is_authenticated:
        return False
    elif principal.is_superuser:
        return True
    elif (
        BucketPermission.objects.filter(
            bucket=bucket,
            team_id__in=principal.team_set.all().values("id"),
            mode__in=[PermissionMode.EDITOR, PermissionMode.OWNER],
        ).count()
        > 0
    ):
        return True
    else:
        return False
