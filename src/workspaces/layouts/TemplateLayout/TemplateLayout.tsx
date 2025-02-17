import { gql } from "@apollo/client";
import { TrashIcon } from "@heroicons/react/24/outline";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import { useState } from "react";
import { useTranslation } from "next-i18next";
import TabLayout from "../TabLayout";
import { GetServerSidePropsContext } from "next";
import { CustomApolloClient } from "core/helpers/apollo";
import {
  TemplateLayout_TemplateFragment,
  TemplateLayout_WorkspaceFragment,
} from "./TemplateLayout.generated";
import DeleteTemplateDialog from "pipelines/features/DeleteTemplateDialog";
import router from "next/router";
import WorkspaceLayout from "../WorkspaceLayout";
import Title from "core/components/Title";

type TemplateLayoutProps = {
  template: TemplateLayout_TemplateFragment;
  workspace: TemplateLayout_WorkspaceFragment;
  currentTab?: string;
  extraBreadcrumbs?: { href: string; title: string }[];
  children: React.ReactElement;
};

const TemplateLayout = (props: TemplateLayoutProps) => {
  const { children, workspace, template, extraBreadcrumbs = [] } = props;

  const { t } = useTranslation();
  const [isDeleteTemplateDialogOpen, setDeleteTemplateDialogOpen] =
    useState(false);

  return (
    <WorkspaceLayout
      workspace={workspace}
      header={
        <>
          <Breadcrumbs withHome={false} className="flex-1">
            <Breadcrumbs.Part
              isFirst
              href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
            >
              {workspace.name}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
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
          {template.permissions.delete && (
            <Button
              onClick={() => setDeleteTemplateDialogOpen(true)}
              className="bg-red-700 hover:bg-red-700 focus:ring-red-500"
              leadingIcon={<TrashIcon className="w-4" />}
            >
              {t("Delete")}
            </Button>
          )}
        </>
      }
    >
      <WorkspaceLayout.PageContent>
        <Title level={2}>{template.name ?? t("Template")}</Title>
        {children}
      </WorkspaceLayout.PageContent>
      <DeleteTemplateDialog
        open={isDeleteTemplateDialogOpen}
        onClose={() => {
          setDeleteTemplateDialogOpen(false);
          router
            .push(`/workspaces/${workspace.slug}/pipelines/?tab=templates`)
            .then();
        }}
        pipelineTemplate={template}
      />
    </WorkspaceLayout>
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
      }
    }
  `,
};

export default TemplateLayout;
