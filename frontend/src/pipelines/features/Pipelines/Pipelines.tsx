import React, { useState } from "react";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import Button from "core/components/Button";
import PipelineCard from "workspaces/features/PipelineCard";
import Pagination from "core/components/Pagination";
import { gql } from "@apollo/client";
import { Pipelines_WorkspaceFragment } from "./Pipelines.generated";
import { useWorkspacePipelinesPageQuery } from "workspaces/graphql/queries.generated";

type PipelinesProps = {
  workspace: Pipelines_WorkspaceFragment;
  setDialogOpen: (open: boolean) => void;
};

const Pipelines = ({ workspace, setDialogOpen }: PipelinesProps) => {
  const { t } = useTranslation();
  const router = useRouter();
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);

  const { data } = useWorkspacePipelinesPageQuery({
    variables: {
      workspaceSlug: workspace.slug,
      page,
      perPage,
    },
  });

  if (!data?.workspace) {
    return null;
  }

  const { pipelines } = data;

  return pipelines.items.length === 0 ? (
    <div className="text-center text-gray-500">
      <div>{t("This workspace does not have any pipeline.")}</div>
      <Button
        variant="secondary"
        onClick={() => setDialogOpen(true)}
        className="mt-4"
      >
        {t("Add a new pipeline")}
      </Button>
    </div>
  ) : (
    <>
      <div className="mt-5 mb-3 grid grid-cols-2 gap-4 xl:grid-cols-3 xl:gap-5">
        {pipelines.items.map((pipeline, index) => (
          <PipelineCard workspace={workspace} key={index} pipeline={pipeline} />
        ))}
      </div>
      <Pagination
        onChange={(page, perPage) => {
          setPage(page);
          setPerPage(perPage);
          router
            .push({
              pathname: "/workspaces/[workspaceSlug]/pipelines",
              query: {
                page,
                perPage,
                workspaceSlug: workspace.slug,
              },
            })
            .then();
        }}
        page={page}
        perPage={perPage}
        totalItems={pipelines.totalItems}
        countItems={pipelines.items.length}
      />
    </>
  );
};

const GET_PIPELINES = gql`
  query GetPipelines($page: Int!, $perPage: Int!, $workspaceSlug: String) {
    pipelines(page: $page, perPage: $perPage, workspaceSlug: $workspaceSlug) {
      pageNumber
      totalPages
      totalItems
      items {
        id
        description
        code
        name
        permissions {
          delete
        }
        currentVersion {
          id
          versionNumber
          createdAt
          user {
            ...User_user
          }
        }
      }
    }
  }
`;

Pipelines.fragments = {
  workspace: gql`
    fragment Pipelines_workspace on Workspace {
      slug
    }
  `,
};

export default Pipelines;
