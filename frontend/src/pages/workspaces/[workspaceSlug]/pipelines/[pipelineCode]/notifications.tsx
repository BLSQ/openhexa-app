import { ExclamationCircleIcon } from "@heroicons/react/24/outline";
import DataCard from "core/components/DataCard";
import SelectProperty from "core/components/DataCard/SelectProperty";
import SwitchProperty from "core/components/DataCard/SwitchProperty";
import Page from "core/components/Page";
import Tooltip from "core/components/Tooltip";
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

  // Only a scheduled zipfile pipeline is at risk: notebooks take no parameters, and a manual run
  // still prompts the user for the missing values.
  const missingScheduleParameters =
    pipeline.schedule && pipeline.type === PipelineType.ZipFile
      ? (versionToRun?.missingScheduleParameters ?? [])
      : [];

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
          title={
            <>
              <h4 className="font-medium">{t("Scheduling")}</h4>
              {pipeline.permissions.update &&
                missingScheduleParameters.length > 0 && (
                  <Tooltip
                    className="flex items-center"
                    label={t(
                      "Scheduled runs are being skipped: the required parameters {{parameters}} have no value. Set their default values to fix the problem.",
                      { parameters: missingScheduleParameters.join(", ") },
                    )}
                  >
                    <ExclamationCircleIcon className="inline-block w-6 h-6 text-yellow-500 ml-1.5" />
                  </Tooltip>
                )}
            </>
          }
          onSave={pipeline.permissions.update ? onSaveScheduling : undefined}
          collapsible={false}
        >
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
