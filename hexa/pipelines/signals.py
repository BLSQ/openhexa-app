from django.db.models.signals import post_delete
from django.dispatch import receiver

from hexa.workspaces.models import WorkspaceMembership

from .models import Pipeline, PipelineRecipient


@receiver(post_delete, sender=WorkspaceMembership, dispatch_uid="delete_member_handler")
def delete_member_handler(sender: type, instance: WorkspaceMembership, **kwargs):
    try:
        # filter pipelines which the user has been added as recipient for the current workspace
        pipelines: Pipeline = Pipeline.objects.filter(
            workspace=instance.workspace, recipients=instance.user
        )
        PipelineRecipient.objects.filter(
            user=instance.user, pipeline__in=pipelines
        ).delete()
    except PipelineRecipient.DoesNotExist:
        pass
