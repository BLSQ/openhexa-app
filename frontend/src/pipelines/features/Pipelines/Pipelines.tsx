import React, { useState } from "react";
import { useTranslation } from "next-i18next";
import Button from "core/components/Button";
import { gql } from "@apollo/client";
import { Pipelines_WorkspaceFragment } from "./Pipelines.generated";
import { useWorkspacePipelinesPageQuery } from "workspaces/graphql/queries.generated";
import Header from "../PipelineTemplates/Header";
import GridView from "./GridView";
import CardView from "./CardView";

type PipelinesProps = {
  workspace: Pipelines_WorkspaceFragment;
  setDialogOpen: (open: boolean) => void;
};

// TODO : search and wiring
// TODO : default and invert
// TODO : name - code -version - type - created at

const Pipelines = ({ workspace, setDialogOpen }: PipelinesProps) => {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState("");
  const [view, setView] = useState<"grid" | "card">("grid");
  const [page, setPage] = useState(1);
  const perPage = 10;

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

  const ViewComponent = view === "grid" ? GridView : CardView;

  return (
    <div>
      <Header
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        view={view}
        setView={setView}
      />
      {pipelines.items.length === 0 ? (
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
        <ViewComponent
          items={pipelines.items}
          workspace={workspace}
          page={page}
          perPage={perPage}
          totalItems={pipelines.totalItems}
          setPage={setPage}
        />
      )}
    </div>
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
