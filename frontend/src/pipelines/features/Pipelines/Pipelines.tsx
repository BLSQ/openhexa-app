import React, { useState } from "react";
import { gql } from "@apollo/client";
import {
  Pipelines_WorkspaceFragment,
  useGetPipelinesQuery,
} from "./Pipelines.generated";
import Header from "../PipelineTemplates/Header";
import GridView from "./GridView";
import CardView from "./CardView";
import useDebounce from "core/hooks/useDebounce";

type PipelinesProps = {
  workspace: Pipelines_WorkspaceFragment;
};

const Pipelines = ({ workspace }: PipelinesProps) => {
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 300);
  const [view, setView] = useState<"grid" | "card">("grid");
  const [page, setPage] = useState(1);
  const perPage = 10;

  const { data } = useGetPipelinesQuery({
    variables: {
      workspaceSlug: workspace.slug,
      name: debouncedSearchQuery,
      page,
      perPage,
    },
  });

  const ViewComponent = view === "grid" ? GridView : CardView;

  const { items, totalItems } = data?.pipelines ?? {
    items: [],
    totalItems: 0,
  };

  return (
    <div>
      <Header
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        view={view}
        setView={setView}
        showCard={true}
      />
      <ViewComponent
        items={items}
        workspace={workspace}
        page={page}
        perPage={perPage}
        totalItems={totalItems}
        setPage={setPage}
      />
    </div>
  );
};

const GET_PIPELINES = gql`
  query GetPipelines(
    $page: Int!
    $perPage: Int!
    $name: String
    $workspaceSlug: String
  ) {
    pipelines(
      page: $page
      perPage: $perPage
      name: $name
      workspaceSlug: $workspaceSlug
    ) {
      pageNumber
      totalPages
      totalItems
      items {
        ...PipelineCard_pipeline
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
