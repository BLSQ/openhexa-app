import React from "react";
import { useRouter } from "next/router";
import { gql, useQuery } from "@apollo/client";
import OrganizationLayout from "./OrganizationLayout";

const ORGANIZATION_QUERY = gql`
  query Organization($id: UUID!) {
    organization(id: $id) {
      id
      name
      shortName
      workspaces {
        items {
          slug
          name
        }
      }
    }
  }
`;

// TODO : orgs for user only
// TODO : get is mac
// TODO : clean UIs
// TODO : clean code

// TODO : All workspaces to BLSQ + all users
// TODO : Feature flag
// TODO : check auth required for org pages

const OrganizationPage = () => {
  const router = useRouter();
  const { organizationId } = router.query;

  const { data } = useQuery(ORGANIZATION_QUERY, {
    variables: { id: organizationId },
    skip: !organizationId,
  });

  const organization = data?.organization || {
    id: organizationId,
    name: "",
    workspaces: { items: [] },
  };

  return (
    <OrganizationLayout organization={organization}>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">{organization.name}</h1>
        <ul>
          {organization.workspaces.items.map((workspace: any) => (
            <li key={workspace.slug} className="mb-2">
              <a
                href={`/workspaces/${workspace.slug}`}
                className="text-blue-600 hover:underline"
              >
                {workspace.name}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </OrganizationLayout>
  );
};

export default OrganizationPage;
