import logging

from django.core.exceptions import PermissionDenied
from django.db.models.signals import post_save
from django.dispatch import receiver

from hexa.pipeline_templates.models import PipelineTemplateVersion
from hexa.pipelines.models import Pipeline

logger = logging.getLogger(__name__)


@receiver(
    post_save,
    sender=PipelineTemplateVersion,
    dispatch_uid="auto_update_pipelines_from_template",
)
def auto_update_pipelines_from_template(sender, instance, created, **kwargs):
    """
    Automatically update pipelines when a new template version is created
    if the workspace has auto_update_pipelines_from_template enabled.

    This signal is triggered whenever a PipelineTemplateVersion is saved.
    It only processes newly created versions (not updates to existing ones).
    """
    if not created:
        logger.debug(
            "Signal ignored: PipelineTemplateVersion was updated, not created."
        )
        return

    template = instance.template

    principal = instance.user
    if not principal:
        principal = template.source_pipeline.workspace.created_by
        logger.debug(
            f"Using workspace creator as principal for system-generated template version: {principal}"
        )

    if not principal:
        logger.debug(
            "Signal ignored: No principal available for auto-update operations."
        )
        return
    logger.debug(
        f"New template version created: {template.name} v{instance.version_number}"
    )

    pipelines_to_update = Pipeline.objects.filter(
        source_template=template,
        workspace__auto_update_pipelines_from_template=True,
        deleted_at__isnull=True,
    ).select_related("workspace")

    if not pipelines_to_update.exists():
        logger.debug(f"No pipelines to auto-update for template '{template.name}'")
        return

    updated_pipelines = []
    failed_pipelines = []

    for pipeline in pipelines_to_update:
        try:
            instance.create_pipeline_version(
                principal=principal,
                workspace=pipeline.workspace,
                pipeline=pipeline,
            )
            updated_pipelines.append(pipeline)
        except PermissionDenied as e:
            failed_pipelines.append((pipeline, f"Permission denied: {e}"))
            logger.warning(
                f"Permission denied when auto-updating pipeline '{pipeline.name}' in workspace '{pipeline.workspace.name}': {e}"
            )
        except Exception as e:
            failed_pipelines.append((pipeline, str(e)))
            logger.error(
                f"Failed to auto-update pipeline '{pipeline.name}' in workspace '{pipeline.workspace.name}': {e}",
                exc_info=True,
            )

    if updated_pipelines:
        logger.info(
            f"Successfully auto-updated {len(updated_pipelines)} pipelines from template '{template.name}' v{instance.version_number}"
        )

    if failed_pipelines:
        logger.error(
            f"Failed to auto-update {len(failed_pipelines)} pipelines from template '{template.name}' v{instance.version_number}"
        )
