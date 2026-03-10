import { gql } from "@apollo/client";
import { EyeIcon, TrashIcon } from "@heroicons/react/24/outline";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import Link from "next/link";
import { useState } from "react";
import { useTranslation } from "next-i18next";
import DeleteWebappDialog from "workspaces/features/DeleteWebappDialog/DeleteWebappDialog";
import TabLayout from "../TabLayout";
import { GetServerSidePropsContext } from "next";
import { CustomApolloClient } from "core/helpers/apollo";
import {
  WebappLayout_WebappFragment,
  WebappLayout_WorkspaceFragment,
} from "./WebappLayout.generated";
import { WebappType } from "graphql/types";

type WebappLayoutProps = {
  webapp: WebappLayout_WebappFragment;
  workspace: WebappLayout_WorkspaceFragment;
  currentTab?: string;
  extraActions?: React.ReactNode;
  children: React.ReactNode;
};

const WebappLayout = (props: WebappLayoutProps) => {
  const {
    children,
    workspace,
    webapp,
    currentTab = "general",
    extraActions,
  } = props;

  const { t } = useTranslation();
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  const isGitWebapp =
    webapp.type === WebappType.Html || webapp.type === WebappType.Bundle;

  const tabs = [
    {
      label: t("General"),
      href: `/workspaces/${encodeURIComponent(workspace.slug)}/webapps/${encodeURIComponent(webapp.slug)}`,
      id: "general",
    },
    ...(isGitWebapp
      ? [
          {
            label: t("Code"),
            href: `/workspaces/${encodeURIComponent(workspace.slug)}/webapps/${encodeURIComponent(webapp.slug)}/code`,
            id: "code",
          },
        ]
      : []),
  ];

  return (
    <TabLayout
      workspace={workspace}
      item={webapp}
      currentTab={currentTab}
      tabs={tabs}
      title={webapp.name}
      header={
        <Breadcrumbs withHome={false} className="flex-1">
          <Breadcrumbs.Part
            isFirst
            href={`/workspaces/${encodeURIComponent(workspace.slug)}/webapps`}
          >
            {t("Web Apps")}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            isLast
            href={`/workspaces/${encodeURIComponent(workspace.slug)}/webapps/${encodeURIComponent(webapp.slug)}`}
          >
            {webapp.name}
          </Breadcrumbs.Part>
        </Breadcrumbs>
      }
      headerActions={
        <div className="flex items-center gap-2">
          {extraActions}
          <Link
            href={
              webapp.type === WebappType.Superset
                ? webapp.url ?? "#"
                : `/workspaces/${encodeURIComponent(workspace.slug)}/webapps/${encodeURIComponent(webapp.slug)}/play`
            }
            target={webapp.type === WebappType.Superset ? "_blank" : undefined}
          >
            <Button
              variant="primary"
              leadingIcon={<EyeIcon className="h-4 w-4" />}
            >
              {t("View")}
            </Button>
          </Link>
          {webapp.permissions.delete && (
            <Button
              variant="danger"
              leadingIcon={<TrashIcon className="h-4 w-4" />}
              onClick={() => setIsDeleteDialogOpen(true)}
            >
              {t("Delete")}
            </Button>
          )}
        </div>
      }
    >
      {children}
      <DeleteWebappDialog
        open={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        webapp={webapp}
        workspace={workspace}
      />
    </TabLayout>
  );
};

WebappLayout.prefetch = async (
  ctx: GetServerSidePropsContext,
  client: CustomApolloClient,
) => {
  await TabLayout.prefetch(ctx, client);
};

WebappLayout.fragments = {
  workspace: gql`
    fragment WebappLayout_workspace on Workspace {
      slug
      ...TabLayout_workspace
    }
    ${TabLayout.fragments.workspace}
  `,
  webapp: gql`
    fragment WebappLayout_webapp on Webapp {
      id
      slug
      name
      url
      type
      permissions {
        update
        delete
      }
    }
  `,
};

export default WebappLayout;
