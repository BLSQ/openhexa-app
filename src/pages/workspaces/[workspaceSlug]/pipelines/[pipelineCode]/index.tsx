import { InformationCircleIcon } from "@heroicons/react/24/outline";
import Badge from "core/components/Badge";
import Button from "core/components/Button";
import Clipboard from "core/components/Clipboard";
import DataCard from "core/components/DataCard";
import RenderProperty from "core/components/DataCard/RenderProperty";
import TextProperty from "core/components/DataCard/TextProperty";
import Link from "core/components/Link";
import Page from "core/components/Page";
import Switch from "core/components/Switch";
import Tooltip from "core/components/Tooltip";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { PipelineType } from "graphql/types";
import useFeature from "identity/hooks/useFeature";
import { useTranslation } from "next-i18next";
import PipelineVersionParametersTable from "pipelines/features/PipelineVersionParametersTable";
import { useState } from "react";
import GeneratePipelineWebhookUrlDialog from "workspaces/features/GeneratePipelineWebhookUrlDialog";
import PipelineVersionConfigDialog from "workspaces/features/PipelineVersionConfigDialog";
import {
  useWorkspacePipelinePageQuery,
  WorkspacePipelinePageDocument,
  WorkspacePipelinePageQuery,
  WorkspacePipelinePageQueryVariables,
} from "workspaces/graphql/queries.generated";
import {
  formatPipelineType,
  updatePipeline,
} from "workspaces/helpers/pipelines";
import PipelineLayout from "workspaces/layouts/PipelineLayout";
import UpgradePipelineFromTemplateDialog from "pipelines/features/UpgradePipelineFromTemplateDialog";
import useCacheKey from "core/hooks/useCacheKey";

type Props = {
  pipelineCode: string;
  workspaceSlug: string;
};

const WorkspacePipelinePage: NextPageWithLayout = (props: Props) => {
  const { pipelineCode, workspaceSlug } = props;
  const { t } = useTranslation();

  const [isVersionConfigDialogOpen, setVersionConfigDialogOpen] =
    useState(false);
  const [isGenerateWebhookUrlDialogOpen, setIsGenerateWebhookUrlDialogOpen] =
    useState(false);
  const [isUpgradeFromTemplateDialogOpen, setUpgradeFromTemplateDialogOpen] =
    useState(false);
  const [isWebhookFeatureEnabled] = useFeature("pipeline_webhook");
  const [isPipelineTemplateFeatureEnabled] = useFeature("pipeline_templates");

  const { data, refetch } = useWorkspacePipelinePageQuery({
    variables: {
      workspaceSlug,
      pipelineCode,
    },
  });
  const clearCache = useCacheKey(["pipelines"], refetch);

  if (!data?.workspace || !data?.pipeline) {
    return null;
  }

  const { workspace, pipeline } = data;

  const onSavePipeline = async (values: any) => {
    await updatePipeline(pipeline.id, {
      name: values.name,
      description: values.description,
    });
  };

  const onSaveWebhook = async (values: any) => {
    await updatePipeline(pipeline.id, {
      webhookEnabled: values.webhookEnabled,
    });
  };

  return (
    <Page title={pipeline.name ?? t("Pipeline")}>
      <PipelineLayout workspace={workspace} pipeline={pipeline}>
        <DataCard.FormSection
          title={t("Information")}
          onSave={pipeline.permissions.update ? onSavePipeline : undefined}
          collapsible={false}
        >
          <TextProperty
            id="description"
            accessor={"description"}
            label={t("Description")}
            defaultValue="-"
            visible={(value, isEditing) => isEditing || value}
            sm
            hideLabel
            markdown
          />
          <TextProperty
            id="name"
            accessor={"name"}
            label={t("Name")}
            visible={(value, isEditing) => isEditing}
          />
          <TextProperty
            id="code"
            accessor={"code"}
            label={t("Code")}
            help={t(
              "This is the code used to identify this pipeline using the cli.",
            )}
            readonly
          />
          <RenderProperty id="type" label={t("Type")} accessor="type">
            {(property) => (
              <Badge className="bg-gray-50 ring-gray-500/20">
                {formatPipelineType(property.displayValue)}
              </Badge>
            )}
          </RenderProperty>
          {pipeline.type === PipelineType.Notebook && (
            <>
              <RenderProperty
                id="notebookPath"
                accessor={"notebookPath"}
                label={t("Notebook path")}
                readonly
              >
                {(property) => (
                  <div className="flex items-center gap-1.5 text-xs">
                    <Clipboard value={property.displayValue}>
                      <Link
                        customStyle="hover:opacity-80"
                        href={`/workspaces/${encodeURIComponent(
                          workspace.slug,
                        )}/files/${property.displayValue.split("/").slice(0, -1).join("/")}`}
                      >
                        <code>{property.displayValue}</code>
                      </Link>
                    </Clipboard>
                  </div>
                )}
              </RenderProperty>
            </>
          )}
          {pipeline.type === PipelineType.ZipFile && (
            <RenderProperty
              id="version_name"
              accessor={"currentVersion"}
              label={t("Version")}
              readonly
            >
              {(property) => (
                <div className="flex items-center gap-3">
                  <Link
                    href={`/workspaces/${encodeURIComponent(
                      workspace.slug,
                    )}/pipelines/${encodeURIComponent(pipeline.code)}/versions`}
                  >
                    {property.displayValue
                      ? property.displayValue.versionName
                      : t("No version yet")}
                  </Link>
                </div>
              )}
            </RenderProperty>
          )}
          {isPipelineTemplateFeatureEnabled && pipeline.sourceTemplate && (
            <RenderProperty
              id="source_template"
              accessor={"sourceTemplate.name"}
              label={t("Source Template")}
              readonly
            >
              {(sourceTemplateName) => (
                <div className="flex items-center gap-2">
                  <Link
                    href={`/workspaces/${encodeURIComponent(
                      workspace.slug,
                    )}/templates/${pipeline.sourceTemplate?.code}`}
                  >
                    {sourceTemplateName.displayValue}
                  </Link>
                  {pipeline.hasNewTemplateVersions &&
                    pipeline.permissions.createVersion && (
                      <Button
                        variant={"secondary"}
                        size={"sm"}
                        onClick={() => setUpgradeFromTemplateDialogOpen(true)}
                      >
                        {t("Upgrade to latest version")}
                      </Button>
                    )}
                </div>
              )}
            </RenderProperty>
          )}
          {isPipelineTemplateFeatureEnabled && pipeline?.template && (
            <RenderProperty
              id="template"
              accessor={"template.name"}
              label={t("Template")}
              readonly
            >
              {(templateName) => (
                <Link
                  href={`/workspaces/${encodeURIComponent(
                    workspace.slug,
                  )}/templates/${pipeline?.template?.code}`}
                >
                  {templateName.displayValue}
                </Link>
              )}
            </RenderProperty>
          )}
        </DataCard.FormSection>
        {pipeline.type === PipelineType.ZipFile && pipeline.currentVersion ? (
          <DataCard.Section title={t("Parameters")} collapsible={false}>
            {pipeline.currentVersion.parameters.length > 0 ? (
              <>
                <div className="flex justify-end">
                  {pipeline.permissions.update && (
                    <Button
                      variant="white"
                      className="mb-4"
                      onClick={() => setVersionConfigDialogOpen(true)}
                    >
                      {t("Set default values")}
                    </Button>
                  )}
                </div>
                <div className="rounded-md overflow-hidden border border-gray-100">
                  <PipelineVersionParametersTable
                    version={pipeline.currentVersion}
                  />
                </div>
                <PipelineVersionConfigDialog
                  version={pipeline.currentVersion}
                  open={isVersionConfigDialogOpen}
                  onClose={() => setVersionConfigDialogOpen(false)}
                />
              </>
            ) : (
              <div className="italic text-sm text-gray-500">
                {t("This pipeline has no parameters.")}
              </div>
            )}
          </DataCard.Section>
        ) : (
          <></>
        )}
        {isWebhookFeatureEnabled ? (
          <DataCard.FormSection
            title={
              <div className="flex items-center">
                {t("Webhook")}{" "}
                <Tooltip
                  placement="top"
                  renderTrigger={(ref) => (
                    <span ref={ref} data-testid="help">
                      <InformationCircleIcon className="ml-1 h-3 w-3 cursor-pointer" />
                    </span>
                  )}
                  label={t(
                    "You can use a webhook to trigger this pipeline from an external system using a POST request.",
                  )}
                />
              </div>
            }
            defaultOpen={false}
            onSave={pipeline.permissions.update ? onSaveWebhook : undefined}
            collapsible={false}
          >
            <RenderProperty
              label={t("Enabled")}
              id="webhookEnabled"
              accessor="webhookEnabled"
            >
              {(property, section) => (
                <div className="flex items-center gap-2">
                  <Switch
                    checked={property.formValue}
                    onChange={property.setValue}
                  />
                  {section.isEdited && (
                    <span className="text-xs text-gray-500">
                      {t(
                        "Anyone with the URL will be able to trigger this pipeline",
                      )}
                    </span>
                  )}
                </div>
              )}
            </RenderProperty>
            <RenderProperty
              visible={(_, isEdited) => Boolean(pipeline.webhookUrl)}
              readonly
              id="webhookUrl"
              label={t("URL")}
              accessor="webhookUrl"
            >
              {(property, section) => (
                <div className="flex items-center gap-2">
                  <code className="text-xs max-w-[100ch] text-ellipsis overflow-x-hidden">
                    {property.displayValue}
                  </code>
                  {!section.isEdited && (
                    <Clipboard value={property.displayValue} />
                  )}
                  {section.isEdited && (
                    <>
                      <Button
                        className="whitespace-nowrap"
                        variant="secondary"
                        size="sm"
                        onClick={() => setIsGenerateWebhookUrlDialogOpen(true)}
                      >
                        {t("Generate a new URL")}
                      </Button>
                      <GeneratePipelineWebhookUrlDialog
                        onClose={() => setIsGenerateWebhookUrlDialogOpen(false)}
                        pipeline={pipeline}
                        open={isGenerateWebhookUrlDialogOpen}
                      />
                    </>
                  )}
                </div>
              )}
            </RenderProperty>
          </DataCard.FormSection>
        ) : (
          <></>
        )}
        <UpgradePipelineFromTemplateDialog
          pipeline={pipeline}
          open={isUpgradeFromTemplateDialogOpen}
          onClose={() => setUpgradeFromTemplateDialogOpen(false)}
          onSuccess={clearCache}
        />
      </PipelineLayout>
    </Page>
  );
};

WorkspacePipelinePage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await PipelineLayout.prefetch(ctx, client);

    const { data } = await client.query<
      WorkspacePipelinePageQuery,
      WorkspacePipelinePageQueryVariables
    >({
      query: WorkspacePipelinePageDocument,
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

export default WorkspacePipelinePage;
