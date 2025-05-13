import React, { useEffect, useState } from "react";
import { gql } from "@apollo/client";
import { Pipelines_WorkspaceFragment } from "./Pipelines.generated";
import Header from "../PipelineTemplates/Header";
import GridView from "./GridView";
import CardView from "./CardView";
import useDebounce from "core/hooks/useDebounce";
import Spinner from "core/components/Spinner";
import { useWorkspacePipelinesPageQuery } from "workspaces/graphql/queries.generated";

type PipelinesProps = {
  workspace: Pipelines_WorkspaceFragment;
};

const Pipelines = ({ workspace }: PipelinesProps) => {
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 300);
  const [view, setView] = useState<"grid" | "card">("grid");
  const [page, setPage] = useState(1);
  const perPage = 10;

  const { data, loading } = useWorkspacePipelinesPageQuery({
    variables: {
      workspaceSlug: workspace.slug,
      search: debouncedSearchQuery,
      page,
      perPage,
    },
  });

  const [items, setItems] = useState(data?.pipelines?.items || []);

  useEffect(() => {
    if (!loading && data?.pipelines?.items) {
      setItems(data.pipelines.items);
    }
  }, [loading, data]);

  const ViewComponent = view === "grid" ? GridView : CardView;

  const totalItems = data?.pipelines?.totalItems ?? 0;

  return (
    <div>
      <Header
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        view={view}
        setView={setView}
        showCard={true}
      />
      <div className="relative">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center backdrop-blur-xs z-10">
            <Spinner />
          </div>
        )}
        <ViewComponent
          items={items}
          workspace={workspace}
          page={page}
          perPage={perPage}
          totalItems={totalItems}
          setPage={setPage}
        />
      </div>
    </div>
  );
};

Pipelines.fragments = {
  workspace: gql`
    fragment Pipelines_workspace on Workspace {
      slug
    }
  `,
};

export default Pipelines;
