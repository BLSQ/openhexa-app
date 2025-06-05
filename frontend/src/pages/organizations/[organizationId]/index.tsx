import React from "react";
import { useRouter } from "next/router";
import { gql, useQuery } from "@apollo/client";
import OrganizationLayout from "./OrganizationLayout";

const ORGANIZATION_QUERY = gql`
  query Organization($id: UUID!) {
    organization(id: $id) {
      id
      name
      workspaces {
        items {
          slug
          name
        }
      }
    }
  }
`;

// TODO : Organization layout
// TODO : All workspaces to BLSQ + all users
// TODO : Feature flag
// TODO : list all workspaces
// TODO : beautiful layout
// TODO : check auth required for org pages

const OrganizationLandingPage = () => {
  const router = useRouter();
  const { organizationId } = router.query;

  const { data, loading, error } = useQuery(ORGANIZATION_QUERY, {
    variables: { id: organizationId },
    skip: !organizationId,
  });

  if (loading || !data) return <div>Loading...</div>;
  if (error) return <div>Error loading organization</div>;

  const { organization } = data;

  return (
    <OrganizationLayout organization={organization}>
      <div className="text-center text-xl">Welcome to {organization.name}</div>
    </OrganizationLayout>
  );
};

export default OrganizationLandingPage;
