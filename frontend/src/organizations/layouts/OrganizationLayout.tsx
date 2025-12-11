import React from "react";
import OrganizationSidebar from "./Sidebar/OrganizationSidebar";
import { GetServerSidePropsContext } from "next";
import { OrganizationQuery } from "organizations/graphql/queries.generated";
import BaseLayout from "./BaseLayout";

type OrganizationLayoutProps = {
  children: React.ReactNode;
  organization: OrganizationQuery["organization"];
  header?: React.ReactNode;
  headerActions?: React.ReactNode;
};

const OrganizationLayout = ({
  children,
  organization,
  header,
  headerActions,
}: OrganizationLayoutProps) => {
  return (
    <BaseLayout
      Sidebar={OrganizationSidebar}
      sidebarProps={{ organization }}
      organizationId={organization?.id}
      header={header}
      headerActions={headerActions}
    >
      {children}
    </BaseLayout>
  );
};

OrganizationLayout.prefetch = async (ctx: GetServerSidePropsContext) => {
  await BaseLayout.prefetch(ctx);
};

export default OrganizationLayout;
