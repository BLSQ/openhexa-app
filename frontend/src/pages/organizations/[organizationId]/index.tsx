import { gql, useQuery } from "@apollo/client";
import { useRouter } from "next/router";
import React, { useState } from "react";
import Spinner from "core/components/Spinner";
import Link from "core/components/Link";
import { useTranslation } from "next-i18next";

// TODO : landing page with search

const ORGANIZATION_QUERY = gql`
  query Organization($id: UUID!) {
    organization(id: $id) {
      id
      name
      workspaces {
        items {
          name
        }
      }
    }
  }
`;

const OrganizationLandingPage = () => {
  const router = useRouter();
  const { organizationId } = router.query;
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState("");

  const { data, loading, error } = useQuery(ORGANIZATION_QUERY, {
    variables: { id: organizationId },
    skip: !organizationId,
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return <p className="text-red-500">{t("Error loading organization")}</p>;
  }

  console.log(organizationId, loading, error);
  // const { organization } = data;
  //
  // const filteredWorkspaces = organization.workspaces.filter((workspace: any) =>
  //   workspace.name.toLowerCase().includes(searchTerm.toLowerCase()),
  // );

  return (
    <> Hello </>
    // <div className="container mx-auto px-4 py-8">
    //   <h1 className="text-2xl font-bold mb-4">{organization.name}</h1>
    //   <div className="mb-6">
    //     <input
    //       type="text"
    //       placeholder={t("Search workspaces")}
    //       value={searchTerm}
    //       onChange={(e) => setSearchTerm(e.target.value)}
    //       className="w-full px-4 py-2 border border-gray-300 rounded-md"
    //     />
    //   </div>
    //   <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    //     {filteredWorkspaces.map((workspace: any) => (
    //       <Link
    //         key={workspace.id}
    //         href={`/workspaces/${workspace.slug}`}
    //         className="block p-4 border border-gray-300 rounded-md hover:bg-gray-100"
    //       >
    //         <h2 className="text-lg font-semibold">{workspace.name}</h2>
    //       </Link>
    //     ))}
    //   </div>
    // </div>
  );
};

export default OrganizationLandingPage;
