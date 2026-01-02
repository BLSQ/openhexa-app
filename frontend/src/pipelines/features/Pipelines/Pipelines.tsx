import React, { useEffect, useState } from "react";
import { gql } from "@apollo/client";
import { Pipelines_WorkspaceFragment } from "./Pipelines.generated";
import Header from "../PipelineTemplates/Header";
import GridView from "./GridView";
import CardView from "./CardView";
import useDebounce from "core/hooks/useDebounce";
import Spinner from "core/components/Spinner";
import { useWorkspacePipelinesPageQuery } from "workspaces/graphql/queries.generated";
import { PipelineFunctionalType, PipelineRunStatus } from "graphql/types";
import { getCookie, hasCookie, setCookie } from "cookies-next";

export let cookiePipelinesView: "grid" | "card" = "grid";

function getDefaultPipelinesView(): "grid" | "card" {
  if (typeof window === "undefined") {
    return cookiePipelinesView;
  } else if (hasCookie("pipelines-view")) {
    return getCookie("pipelines-view") as "grid" | "card";
  } else {
    return "grid";
  }
}

type PipelinesProps = {
  workspace: Pipelines_WorkspaceFragment;
  page: number;
  perPage: number;
  search: string;
  tags?: string[];
  functionalType?: PipelineFunctionalType | null;
  lastRunStates?: PipelineRunStatus[];
};

const Pipelines = ({
  workspace,
  page: initialPage,
  perPage,
  search: initialSearch,
  tags,
  functionalType: initialFunctionalType,
  lastRunStates: initialLastRunStates,
}: PipelinesProps) => {
  const [searchQuery, setSearchQuery] = useState(initialSearch);
  const debouncedSearchQuery = useDebounce(searchQuery, 300, () => {
    setPage(1); // Reset to first page when debounce completes
  });
  const [view, setView] = useState<"grid" | "card">(getDefaultPipelinesView());
  const [page, setPage] = useState(initialPage);

  const handleSetView = (newView: "grid" | "card") => {
    setView(newView);
    setCookie("pipelines-view", newView, { maxAge: 60 * 60 * 24 * 365 });
  };
  const [functionalType, setFunctionalType] =
    useState<PipelineFunctionalType | null>(initialFunctionalType || null);
  const [lastRunStates, setLastRunStates] = useState<PipelineRunStatus[]>(
    initialLastRunStates || [],
  );
  const [selectedTags, setSelectedTags] = useState<string[]>(tags || []);

  const { data, loading } = useWorkspacePipelinesPageQuery({
    variables: {
      workspaceSlug: workspace.slug,
      search: debouncedSearchQuery,
      tags: selectedTags.length > 0 ? selectedTags : undefined,
      functionalType,
      lastRunStates: lastRunStates.length > 0 ? lastRunStates : undefined,
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

  const pipelineTags = data?.workspace?.pipelineTags || [];
  const pipelineLastRunStatuses =
    data?.workspace?.pipelineLastRunStatuses || [];

  return (
    <div>
      <Header
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        view={view}
        setView={handleSetView}
        showCard={true}
        functionalTypeFilter={functionalType}
        setFunctionalTypeFilter={setFunctionalType}
        lastRunStatesFilter={lastRunStates}
        setLastRunStatesFilter={setLastRunStates}
        tagsFilter={selectedTags}
        setTagsFilter={setSelectedTags}
        pipelineTags={pipelineTags}
        pipelineLastRunStatuses={pipelineLastRunStatuses}
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

Pipelines.prefetch = async (ctx: any) => {
  // Load the cookie value from the request to render it correctly on the server
  cookiePipelinesView = (await hasCookie("pipelines-view", ctx))
    ? ((await getCookie("pipelines-view", ctx)) as "grid" | "card")
    : "grid";
};

export default Pipelines;
