import Breadcrumbs from "core/components/Breadcrumbs";
import LinkTabs from "core/components/Tabs/LinkTabs/LinkTabs";
import { CustomApolloClient } from "core/helpers/apollo";
import { GetServerSidePropsContext } from "next";
import { useTranslation } from "next-i18next";
import { ReactElement, ReactNode } from "react";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import { WorkspaceLayout_WorkspaceFragment } from "workspaces/layouts/WorkspaceLayout/WorkspaceLayout.generated";

export type DataStudioTab = "editor" | "saved";

type DataStudioLayoutProps = {
  workspace: WorkspaceLayout_WorkspaceFragment;
  currentTab: DataStudioTab;
  children: ReactElement | ReactElement[];
  headerActions?: ReactNode;
};

// Shared shell for the Data Studio section: the workspace chrome plus a
// full-width sub-nav (Editor / Saved queries). Both the editor and the saved
// queries list render inside it, so the tab bar stays consistent as the user
// moves between them. Deliberately not built on TabLayout, whose DataCard
// wrapper would fight the full-bleed IDE.
const DataStudioLayout = ({
  workspace,
  currentTab,
  children,
  headerActions,
}: DataStudioLayoutProps) => {
  const { t } = useTranslation();
  const basePath = `/workspaces/${encodeURIComponent(workspace.slug)}/data-studio`;

  const tabs = [
    { id: "editor", label: t("Editor"), href: basePath },
    { id: "saved", label: t("Saved queries"), href: `${basePath}/queries` },
  ];

  return (
    <WorkspaceLayout
      workspace={workspace}
      withMarginBottom={false}
      headerActions={headerActions}
      header={
        <Breadcrumbs withHome={false}>
          <Breadcrumbs.Part isFirst isLast href={basePath}>
            {t("Data Studio")}
          </Breadcrumbs.Part>
        </Breadcrumbs>
      }
    >
      <div className="flex h-[calc(100vh-4rem)] flex-col">
        <div className="shrink-0 border-b border-gray-200 bg-white px-4 md:px-6 xl:px-10 2xl:px-12">
          <LinkTabs tabs={tabs} selected={currentTab} />
        </div>
        <div className="min-h-0 flex-1">{children}</div>
      </div>
    </WorkspaceLayout>
  );
};

DataStudioLayout.prefetch = async (
  ctx: GetServerSidePropsContext,
  client: CustomApolloClient,
) => {
  await WorkspaceLayout.prefetch(ctx, client);
};

export default DataStudioLayout;
