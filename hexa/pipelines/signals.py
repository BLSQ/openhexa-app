from uuid import uuid4

from django.db.models.signals import post_delete
from django.dispatch import receiver

from hexa.workspaces.models import WorkspaceMembership

from .models import PipelineRecipient


@receiver(post_delete, sender=WorkspaceMembership, dispatch_uid=uuid4())
def delete_member_handler(sender: type, instance: WorkspaceMembership, **kwargs):
    try:
        PipelineRecipient.objects.get(user=instance.user).delete()
    except PipelineRecipient.DoesNotExist:
        pass
