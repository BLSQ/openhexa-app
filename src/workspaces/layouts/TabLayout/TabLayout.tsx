import { gql } from "@apollo/client";
import DataCard from "core/components/DataCard";
import React, { ReactElement, ReactNode } from "react";

import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import LinkTabs from "core/components/Tabs/LinkTabs/LinkTabs";
import Title from "core/components/Title";
import { GetServerSidePropsContext } from "next";
import { CustomApolloClient } from "core/helpers/apollo";
import { TabLayout_WorkspaceFragment } from "./TabLayout.generated";

const TabLayoutHeader = ({
  children,
  className,
}: {
  children: ReactNode;
  className: string;
}) => <div className={className}>{children}</div>;

const TabLayoutPageContent = ({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) => <div className={className}>{children}</div>;

type TabLayoutProps = {
  workspace: TabLayout_WorkspaceFragment;
  item: any;
  currentTab: string;
  children: React.ReactNode;
  helpLinks?: { label: string; href: string }[];
  tabs: { label: string; href: string; id: string }[];
  title?: string | ReactElement;
};

const TabLayout = ({
  workspace,
  item,
  currentTab,
  children,
  helpLinks,
  tabs,
  title,
}: TabLayoutProps) => {
  const headerChild = React.Children.toArray(children).find(
    (child) => React.isValidElement(child) && child.type === TabLayout.Header,
  );

  const contentChild = React.Children.toArray(children).find(
    (child) =>
      React.isValidElement(child) && child.type === TabLayout.PageContent,
  );

  return (
    <WorkspaceLayout workspace={workspace} helpLinks={helpLinks}>
      <WorkspaceLayout.Header>{headerChild}</WorkspaceLayout.Header>
      <WorkspaceLayout.PageContent>
        {typeof title === "string" ? (
          <Title level={2} className="flex items-center justify-between">
            {title}
          </Title>
        ) : (
          title
        )}
        <DataCard item={item}>
          <LinkTabs className="mx-4 mt-2" tabs={tabs} selected={currentTab} />
          {contentChild}
        </DataCard>
      </WorkspaceLayout.PageContent>
    </WorkspaceLayout>
  );
};

TabLayout.prefetch = async (
  ctx: GetServerSidePropsContext,
  client: CustomApolloClient,
) => {
  await WorkspaceLayout.prefetch(ctx, client);
};

TabLayout.fragments = {
  workspace: gql`
    fragment TabLayout_workspace on Workspace {
      ...WorkspaceLayout_workspace
      name
    }
    ${WorkspaceLayout.fragments.workspace}
  `,
};

TabLayout.Header = TabLayoutHeader;
TabLayout.PageContent = TabLayoutPageContent;

export default TabLayout;
