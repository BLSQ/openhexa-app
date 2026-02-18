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
import usePipelinesView from "pipelines/hooks/usePipelinesView";
import {
  getPipelineSortOptions,
  pipelineSorting,
  PipelineSortOption,
} from "pipelines/config/sorting";
import { SortingRule } from "react-table";

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
  const [view, setView] = usePipelinesView();
  const [page, setPage] = useState(initialPage);


  const sortOptions = getPipelineSortOptions()
  const [sortOrder, setSortOrder] = useState<PipelineSortOption>(
    sortOptions[0],
  );

  const [functionalType, setFunctionalType] = useState<PipelineFunctionalType | null>(
    initialFunctionalType || null
  );
    const [lastRunStates, setLastRunStates] = useState<PipelineRunStatus[]>(
    initialLastRunStates || [],
  );
  const [selectedTags, setSelectedTags] = useState<string[]>(tags || []);

  const { data, loading } = useWorkspacePipelinesPageQuery({
    variables: {
      page,
      perPage,
      workspaceSlug: workspace.slug,
      search: debouncedSearchQuery,
      tags: selectedTags.length > 0 ? selectedTags : undefined,
      functionalType,
      lastRunStates: lastRunStates.length > 0 ? lastRunStates : undefined,
      orderBy: sortOrder.orderBy,
    },
  });

  const [items, setItems] = useState(data?.pipelines?.items || []);
  const [pipelineTags, setPipelineTags] = useState<string[]>(
    data?.workspace?.pipelineTags || [],
  );
  const [pipelineLastRunStatuses, setPipelineLastRunStatuses] = useState<
    PipelineRunStatus[]
  >(data?.workspace?.pipelineLastRunStatuses || []);

  useEffect(() => {
    if (!loading && data?.pipelines?.items) {
      setItems(data.pipelines.items);
    }
    if (!loading && data?.workspace?.pipelineTags) {
      setPipelineTags(data.workspace.pipelineTags);
    }
    if (!loading && data?.workspace?.pipelineLastRunStatuses) {
      setPipelineLastRunStatuses(data.workspace.pipelineLastRunStatuses);
    }
  }, [loading, data]);

  const handleDataGridSort = (params: {
    page: number;
    pageSize: number;
    pageIndex: number;
    sortBy: SortingRule<object>[];
  }) => {
    const orderBy = pipelineSorting.convertDataGridSort(params.sortBy);
    if (orderBy) {
      const matchingOption = sortOptions.find((opt) => opt.orderBy === orderBy);
      if (matchingOption) {
        setSortOrder(matchingOption);
      }
    }
    setPage(params.page);
  };

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
        functionalTypeFilter={functionalType}
        setFunctionalTypeFilter={setFunctionalType}
        lastRunStatesFilter={lastRunStates}
        setLastRunStatesFilter={setLastRunStates}
        tagsFilter={selectedTags}
        setTagsFilter={setSelectedTags}
        pipelineTags={pipelineTags}
        pipelineLastRunStatuses={pipelineLastRunStatuses}
        sortOrder={sortOrder}
        setSortOrder={setSortOrder}
        sortOptions={sortOptions}
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
          onSort={view === "grid" ? handleDataGridSort : undefined}
          currentSort={view === "grid" ? sortOrder.orderBy : undefined}
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
