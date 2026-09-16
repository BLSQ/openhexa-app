import { ExclamationCircleIcon } from "@heroicons/react/24/outline";
import DataCard from "core/components/DataCard";
import SelectProperty from "core/components/DataCard/SelectProperty";
import SwitchProperty from "core/components/DataCard/SwitchProperty";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { PipelineType } from "graphql/types";
import { useTranslation } from "next-i18next";
import CronProperty from "workspaces/features/CronProperty";
import PipelineRecipients from "workspaces/features/PipelineRecipients";
import {
  useWorkspacePipelineNotificationsPageQuery,
  WorkspacePipelineNotificationsPageDocument,
  WorkspacePipelineNotificationsPageQuery,
  WorkspacePipelineNotificationsPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import { updatePipeline } from "workspaces/helpers/pipelines";
import PipelineLayout from "workspaces/layouts/PipelineLayout";
import Title from "core/components/Title";

type Props = {
  pipelineCode: string;
  workspaceSlug: string;
};

const WorkspacePipelineNotificationsPage: NextPageWithLayout = (
  props: Props,
) => {
  const { pipelineCode, workspaceSlug } = props;
  const { t } = useTranslation();
  const { data } = useWorkspacePipelineNotificationsPageQuery({
    variables: {
      workspaceSlug,
      pipelineCode,
    },
  });

  if (!data?.workspace || !data?.pipeline) {
    return null;
  }

  const { workspace, pipeline } = data;

  // The scheduler runs the pinned version, or the latest one when nothing is pinned.
  const versionToRun =
    pipeline.scheduledPipelineVersion ?? pipeline.currentVersion;

  // Not gated on the pipeline already being scheduled: the point is to say up front that this
  // pipeline cannot run unattended as it stands, rather than to reject the cron on save. Notebooks
  // take no parameters, and a manual run still prompts the user for the missing values.
  const missingScheduleParameters =
    pipeline.type === PipelineType.ZipFile
      ? (versionToRun?.missingScheduleParameters ?? [])
      : [];

  const showMissingParametersWarning =
    pipeline.permissions.update && missingScheduleParameters.length > 0;

  const canEditScheduling =
    pipeline.permissions.update &&
    (Boolean(pipeline.schedule) || missingScheduleParameters.length === 0);

  const versionItems = pipeline.versions?.items ?? [];
  const pinned = pipeline.scheduledPipelineVersion;
  const versionOptions =
    pinned && !versionItems.some((v) => v.id === pinned.id)
      ? [pinned, ...versionItems]
      : versionItems;

  const onSaveScheduling = async (values: any) => {
    const schedulingEnabled = values.enableScheduling;
    await updatePipeline(pipeline.id, {
      schedule: schedulingEnabled ? values.schedule : null,
      ...(schedulingEnabled && {
        scheduledPipelineVersionId: values.scheduledPipelineVersion?.id ?? null,
      }),
    });
  };

  return (
    <Page title={pipeline.name ?? t("Pipeline notifications")}>
      <PipelineLayout
        workspace={workspace}
        pipeline={pipeline}
        currentTab="notifications"
        extraBreadcrumbs={[
          {
            title: t("Scheduling and Notifications"),
            href: `/workspaces/${encodeURIComponent(workspace.slug)}/pipelines/${encodeURIComponent(pipeline.code)}/notifications`,
          },
        ]}
      >
        <DataCard.FormSection
          title={t("Scheduling")}
          onSave={canEditScheduling ? onSaveScheduling : undefined}
          collapsible={false}
        >
          {showMissingParametersWarning && (
            <div className="flex items-start gap-2 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
              <ExclamationCircleIcon className="mt-0.5 h-5 w-5 shrink-0 text-amber-500" />
              <span>
                {t(
                  "The required parameter {{parameters}} has no value, so this pipeline cannot run on a schedule. Set a default value to fix this.",
                  {
                    count: missingScheduleParameters.length,
                    parameters: missingScheduleParameters.join(", "),
                  },
                )}
              </span>
            </div>
          )}
          <SwitchProperty
            id="enableScheduling"
            label={t("Enabled")}
            accessor={(item) => {
              return Boolean(item.schedule);
            }}
          />
          <CronProperty
            id="schedule"
            accessor="schedule"
            label={t("Schedule")}
            help={t("The schedule value should follow the CRON syntax.")}
            placeholder="0 15 * * *"
            visible={(_, __, values) =>
              Boolean(values.enableScheduling || pipeline.schedule)
            }
            required={(_, __, values) => Boolean(values.enableScheduling)}
          />
          {pipeline.type === PipelineType.ZipFile && (
            <SelectProperty
              id="scheduledPipelineVersion"
              accessor="scheduledPipelineVersion"
              label={t("Version")}
              help={t(
                "Choose which version to run on schedule. Leave empty to always run the latest version.",
              )}
              options={versionOptions}
              nullable
              defaultValue={t("Latest version")}
              getOptionLabel={(v) =>
                v.missingScheduleParameters.length > 0
                  ? t("{{version}} (missing parameter values)", {
                      version: v.versionName,
                    })
                  : v.versionName
              }
              visible={(_, __, values) =>
                Boolean(values.enableScheduling || pipeline.schedule)
              }
            />
          )}
        </DataCard.FormSection>
        <div>
          <Title level={6} className="px-6 pt-4">
            {t("Notifications")}
          </Title>

          <div className="px-2 -mx-2">
            <PipelineRecipients className="w-full" pipeline={pipeline} />
          </div>
        </div>
      </PipelineLayout>
    </Page>
  );
};

WorkspacePipelineNotificationsPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await PipelineLayout.prefetch(ctx, client);

    const { data } = await client.query<
      WorkspacePipelineNotificationsPageQuery,
      WorkspacePipelineNotificationsPageQueryVariables
    >({
      query: WorkspacePipelineNotificationsPageDocument,
      variables: {
        workspaceSlug: ctx.params!.workspaceSlug as string,
        pipelineCode: ctx.params!.pipelineCode as string,
      },
    });

    if (!data.workspace || !data.pipeline) {
      return { notFound: true };
    }
    return {
      props: {
        workspaceSlug: ctx.params!.workspaceSlug,
        pipelineCode: ctx.params!.pipelineCode,
      },
    };
  },
});

export default WorkspacePipelineNotificationsPage;
