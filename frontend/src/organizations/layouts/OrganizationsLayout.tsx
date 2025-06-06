import React from "react";
import OrganizationsSidebar from "./Sidebar/OrganizationsSidebar";
import { GetServerSidePropsContext } from "next";
import { OrganizationsQuery } from "organizations/graphql/queries.generated";
import BaseLayout from "./BaseLayout";

type OrganizationsLayoutProps = {
  children?: React.ReactNode;
  organizations: OrganizationsQuery["organizations"];
};

const OrganizationsLayout = ({
  children,
  organizations,
}: OrganizationsLayoutProps) => {
  return (
    <BaseLayout Sidebar={OrganizationsSidebar} sidebarProps={{ organizations }}>
      {children}
    </BaseLayout>
  );
};

OrganizationsLayout.prefetch = async (ctx: GetServerSidePropsContext) => {
  await BaseLayout.prefetch(ctx);
};

export default OrganizationsLayout;
