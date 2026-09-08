import { PlayIcon, TrashIcon } from "@heroicons/react/24/outline";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import Page from "core/components/Page";
import Spinner from "core/components/Spinner";
import Tooltip from "core/components/Tooltip";
import useCacheKey from "core/hooks/useCacheKey";
import { CreateTemplateVersionPermissionReason } from "graphql/types";
import { useTranslation } from "next-i18next";
import DownloadPipelineVersion from "pipelines/features/DownloadPipelineVersion";
import PipelineDetail from "pipelines/features/PipelineDetail/PipelineDetail";
import PublishPipelineDialog from "pipelines/features/PublishPipelineDialog";
import { useMemo, useState } from "react";
import DeletePipelineDialog from "workspaces/features/DeletePipelineDialog";
import RunPipelineDialog from "workspaces/features/RunPipelineDialog";
import { useWorkspacePipelineDetailPageQuery } from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type PipelineDetailPageProps = {
  workspaceSlug: string;
  pipelineCode: string;
  // When set, the Runs tab opens on that run instead of the run list.
  runId?: string;
};

const PipelineDetailPage = ({
  workspaceSlug,
  pipelineCode,
  runId,
}: PipelineDetailPageProps) => {
  const { t } = useTranslation();

  const [isDeleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [isPublishDialogOpen, setPublishDialogOpen] = useState(false);

  const { data, refetch } = useWorkspacePipelineDetailPageQuery({
    variables: { workspaceSlug, pipelineCode },
  });
  useCacheKey(["pipelines"], refetch);

  const pipeline = data?.pipeline;

  const createTemplateVersionReasonMessages = useMemo(() => {
    const reasonMessages = {
      [CreateTemplateVersionPermissionReason.PermissionDenied]: t(
        "You lack permissions to publish a new template version.",
      ),
      [CreateTemplateVersionPermissionReason.PipelineIsNotebook]: t(
        "Notebook pipelines cannot be published as templates.",
      ),
      [CreateTemplateVersionPermissionReason.NoNewTemplateVersionAvailable]: t(
        "No new template version available for publishing.",
      ),
      [CreateTemplateVersionPermissionReason.PipelineIsAlreadyFromTemplate]: t(
        "It is not possible to create a template from a pipeline created using a template.",
      ),
    };

    return (pipeline?.permissions.createTemplateVersion.reasons ?? []).map(
      (reason) => reasonMessages[reason],
    );
  }, [pipeline?.permissions.createTemplateVersion.reasons, t]);

  if (!data?.workspace || !pipeline) {
    return null;
  }

  const { workspace } = data;

  return (
    <Page title={pipeline.name ?? t("Pipeline")}>
      <WorkspaceLayout
        workspace={workspace}
        withMarginBottom={false}
        className="h-screen"
        helpLinks={[
          {
            label: t("About pipelines"),
            href: "https://docs.openhexa.com/pipelines/",
          },
          {
            label: t("Writing OpenHEXA pipelines"),
            href: "https://docs.openhexa.com/writing-pipelines/",
          },
        ]}
        header={
          <Breadcrumbs withHome={false} className="flex-1">
            <Breadcrumbs.Part
              isFirst
              href={`/workspaces/${encodeURIComponent(workspace.slug)}/pipelines`}
            >
              {t("Pipelines")}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              isLast
              href={`/workspaces/${encodeURIComponent(workspace.slug)}/pipelines/${encodeURIComponent(pipeline.code)}`}
            >
              {pipeline.name}
            </Breadcrumbs.Part>
          </Breadcrumbs>
        }
        headerActions={
          <div className="flex items-center gap-2">
            <Tooltip
              label={
                !pipeline.permissions.createTemplateVersion.isAllowed
                  ? createTemplateVersionReasonMessages.map((m, index) => (
                      <p key={index}>{m}</p>
                    ))
                  : undefined
              }
              renderTrigger={(ref) => (
                <span ref={ref}>
                  <Button
                    onClick={() => setPublishDialogOpen(true)}
                    variant="white"
                    disabled={
                      !pipeline.permissions.createTemplateVersion.isAllowed
                    }
                    className="whitespace-nowrap"
                  >
                    {pipeline.template
                      ? t("Publish a new Template Version")
                      : t("Publish as Template")}
                  </Button>
                </span>
              )}
            />
            {pipeline.currentVersion && (
              <DownloadPipelineVersion version={pipeline.currentVersion}>
                {({ onClick, isDownloading }) => (
                  <Button
                    onClick={onClick}
                    variant="white"
                    className="whitespace-nowrap"
                  >
                    {isDownloading && <Spinner size="sm" />}
                    {t("Download code")}
                  </Button>
                )}
              </DownloadPipelineVersion>
            )}
            {pipeline.permissions.run && (
              <RunPipelineDialog pipeline={pipeline}>
                {(onClick) => (
                  <Button
                    variant="primary"
                    leadingIcon={<PlayIcon className="h-4 w-4" />}
                    onClick={onClick}
                  >
                    {t("Run")}
                  </Button>
                )}
              </RunPipelineDialog>
            )}
            {pipeline.permissions.delete && (
              <Button
                variant="danger"
                onClick={() => setDeleteDialogOpen(true)}
                leadingIcon={<TrashIcon className="h-4 w-4" />}
              >
                {t("Delete")}
              </Button>
            )}
          </div>
        }
      >
        <div className="h-full min-h-0">
          <PipelineDetail
            workspaceSlug={workspaceSlug}
            pipelineCode={pipelineCode}
            pipeline={pipeline}
            runId={runId}
            showAssistant={workspace.organization?.aiSettings?.enabled ?? false}
            aiBudgetLimitReached={
              workspace.organization?.aiBudgetLimitReached ?? false
            }
            monthlyLimitExceeded={
              data.me?.assistantMonthlyLimitExceeded ?? false
            }
            onRefetch={() => {
              refetch().then();
            }}
          />
        </div>
      </WorkspaceLayout>
      <DeletePipelineDialog
        open={isDeleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        pipeline={pipeline}
        workspace={workspace}
      />
      <PublishPipelineDialog
        open={isPublishDialogOpen}
        onClose={() => setPublishDialogOpen(false)}
        pipeline={pipeline}
        workspace={workspace}
      />
    </Page>
  );
};

export default PipelineDetailPage;
