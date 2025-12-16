import { gql } from "@apollo/client";
import { PlusIcon, TrashIcon } from "@heroicons/react/24/outline";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import { useState } from "react";
import { useTranslation } from "next-i18next";
import { toast } from "react-toastify";
import TabLayout from "../TabLayout";
import { GetServerSidePropsContext } from "next";
import { CustomApolloClient } from "core/helpers/apollo";
import {
  TemplateLayout_TemplateFragment,
  TemplateLayout_WorkspaceFragment,
} from "./TemplateLayout.generated";
import DeleteTemplateDialog from "pipelines/features/DeleteTemplateDialog";
import router from "next/router";
import DownloadTemplateVersion from "pipelines/features/DownloadTemplateVersion";
import Spinner from "core/components/Spinner";
import { useCreatePipelineFromTemplateVersionMutation } from "pipelines/graphql/mutations.generated";
import { CreatePipelineFromTemplateVersionError } from "graphql/types";
import useCacheKey from "core/hooks/useCacheKey";

type TemplateLayoutProps = {
  template: TemplateLayout_TemplateFragment;
  workspace: TemplateLayout_WorkspaceFragment;
  currentTab?: string;
  extraBreadcrumbs?: { href: string; title: string }[];
  children: React.ReactElement;
};

const TemplateLayout = (props: TemplateLayoutProps) => {
  const {
    children,
    workspace,
    template,
    currentTab = "general",
    extraBreadcrumbs = [],
  } = props;

  const { t } = useTranslation();
  const [isDeleteTemplateDialogOpen, setDeleteTemplateDialogOpen] =
    useState(false);
  const [createPipelineFromTemplateVersion] =
    useCreatePipelineFromTemplateVersionMutation();
  const clearCache = useCacheKey(["pipelines"]);

  const createPipeline = () => {
    if (!template.currentVersion) return;

    createPipelineFromTemplateVersion({
      variables: {
        input: {
          pipelineTemplateVersionId: template.currentVersion.id,
          workspaceSlug: workspace.slug,
        },
      },
    })
      .then((result) => {
        const success = result.data?.createPipelineFromTemplateVersion?.success;
        const errors = result.data?.createPipelineFromTemplateVersion?.errors;
        const pipeline =
          result.data?.createPipelineFromTemplateVersion?.pipeline;
        if (success && pipeline) {
          clearCache();
          toast.success(
            t("Successfully created pipeline {{pipelineName}}", {
              pipelineName: pipeline.name,
            }),
          );
          router
            .push(
              `/workspaces/${encodeURIComponent(
                workspace.slug,
              )}/pipelines/${encodeURIComponent(pipeline.code)}`,
            )
            .then();
        } else if (
          errors?.includes(
            CreatePipelineFromTemplateVersionError.PermissionDenied,
          )
        ) {
          toast.error(t("You are not allowed to create a pipeline."));
        } else {
          toast.error(t("Unknown error : Failed to create pipeline"));
        }
      })
      .catch(() => {
        toast.error(t("Failed to create pipeline"));
      });
  };

  return (
    <TabLayout
      workspace={workspace}
      helpLinks={[
        {
          label: t("About templates"),
          href: "https://github.com/BLSQ/openhexa/wiki/User-manual",
        },
      ]}
      item={template}
      currentTab={currentTab}
      tabs={[
        {
          label: t("General"),
          href: `/workspaces/${encodeURIComponent(workspace.slug)}/templates/${encodeURIComponent(template.code)}`,
          id: "general",
        },
      ].concat(
        template.currentVersion
          ? [
              {
                label: t("Code"),
                href: `/workspaces/${encodeURIComponent(workspace.slug)}/templates/${encodeURIComponent(template.code)}/code`,
                id: "code",
              },
            ]
          : [],
      )}
      title={template.name}
      header={
        <>
          <Breadcrumbs withHome={false} className="flex-1">
            <Breadcrumbs.Part
              isFirst
              href={`/workspaces/${encodeURIComponent(workspace.slug)}/pipelines/?tab=templates`}
            >
              {t("Templates")}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              isLast={!extraBreadcrumbs.length}
              href={`/workspaces/${encodeURIComponent(
                workspace.slug,
              )}/templates/${encodeURIComponent(template.code)}`}
            >
              {template.name}
            </Breadcrumbs.Part>
            {extraBreadcrumbs.map(({ href, title }, index) => (
              <Breadcrumbs.Part
                key={index}
                isLast={extraBreadcrumbs.length - 1 == index}
                href={href}
              >
                {title}
              </Breadcrumbs.Part>
            ))}
          </Breadcrumbs>
        </>
      }
      headerActions={
        <div className="flex items-center gap-2">
          {template.currentVersion && (
            <Button
              variant="primary"
              onClick={createPipeline}
              leadingIcon={<PlusIcon className="h-4 w-4" />}
            >
              {t("Create pipeline")}
            </Button>
          )}
          {template.currentVersion && (
            <DownloadTemplateVersion version={template.currentVersion}>
              {({ onClick, isDownloading }) => (
                <Button onClick={onClick} variant="secondary">
                  {isDownloading && <Spinner size="sm" />}
                  {t("Download code")}
                </Button>
              )}
            </DownloadTemplateVersion>
          )}
          {template.permissions.delete && (
            <Button
              onClick={() => setDeleteTemplateDialogOpen(true)}
              className="bg-red-700 hover:bg-red-700 focus:ring-red-500"
              leadingIcon={<TrashIcon className="w-4" />}
            >
              {t("Delete")}
            </Button>
          )}
        </div>
      }
    >
      {children}
      <DeleteTemplateDialog
        open={isDeleteTemplateDialogOpen}
        onDelete={() =>
          router
            .push(`/workspaces/${workspace.slug}/pipelines/?tab=templates`)
            .then()
        }
        onClose={() => {
          setDeleteTemplateDialogOpen(false);
        }}
        pipelineTemplate={template}
      />
    </TabLayout>
  );
};

TemplateLayout.prefetch = async (
  ctx: GetServerSidePropsContext,
  client: CustomApolloClient,
) => {
  await TabLayout.prefetch(ctx, client);
};

TemplateLayout.fragments = {
  workspace: gql`
    fragment TemplateLayout_workspace on Workspace {
      ...TabLayout_workspace
    }
    ${TabLayout.fragments.workspace}
  `,
  template: gql`
    fragment TemplateLayout_template on PipelineTemplate {
      id
      code
      name
      permissions {
        delete
        update
      }
      currentVersion {
        id
        ...DownloadTemplateVersion_version
      }
    }
    ${DownloadTemplateVersion.fragments.version}
  `,
};

export default TemplateLayout;
