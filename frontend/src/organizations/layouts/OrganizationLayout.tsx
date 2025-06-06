import React from "react";
import OrganizationSidebar from "./Sidebar/OrganizationSidebar";
import { GetServerSidePropsContext } from "next";
import { OrganizationQuery } from "organizations/graphql/queries.generated";
import BaseLayout from "./BaseLayout";

type OrganizationLayoutProps = {
  children: React.ReactNode;
  organization: OrganizationQuery["organization"];
};

const OrganizationLayout = ({
  children,
  organization,
}: OrganizationLayoutProps) => {
  return (
    <BaseLayout Sidebar={OrganizationSidebar} sidebarProps={{ organization }}>
      {children}
    </BaseLayout>
  );
};

OrganizationLayout.prefetch = async (ctx: GetServerSidePropsContext) => {
  await BaseLayout.prefetch(ctx);
  await OrganizationSidebar.prefetch(ctx);
};

export default OrganizationLayout;
