import React from "react";
import { gql, useQuery } from "@apollo/client";
import OrganizationsLayout from "./OrganizationsLayout";

const ORGANIZATIONS_QUERY = gql`
  query Organizations {
    organizations {
      id
      name
    }
  }
`;

const OrganizationsPage = () => {
  const { data } = useQuery(ORGANIZATIONS_QUERY);

  const organizations = data?.organizations || [];

  return (
    <OrganizationsLayout organizations={organizations}>
      <p>Empty</p>
    </OrganizationsLayout>
  );
};

export default OrganizationsPage;
