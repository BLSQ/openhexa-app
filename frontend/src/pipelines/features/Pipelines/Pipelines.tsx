import React, { useEffect, useState } from "react";
import { gql } from "@apollo/client";
import { Pipelines_WorkspaceFragment } from "./Pipelines.generated";
import Header from "../PipelineTemplates/Header";
import GridView from "./GridView";
import CardView from "./CardView";
import useDebounce from "core/hooks/useDebounce";
import Spinner from "core/components/Spinner";
import { useWorkspacePipelinesPageQuery } from "workspaces/graphql/queries.generated";
import { PipelineFunctionalType } from "graphql/types";

type PipelinesProps = {
  workspace: Pipelines_WorkspaceFragment;
  page: number;
  perPage: number;
  search: string;
  tags?: string[];
  functionalType?: PipelineFunctionalType | null;
};

const Pipelines = ({
  workspace,
  page: initialPage,
  perPage,
  search: initialSearch,
  tags,
  functionalType: initialFunctionalType,
}: PipelinesProps) => {
  const [searchQuery, setSearchQuery] = useState(initialSearch);
  const debouncedSearchQuery = useDebounce(searchQuery, 300, () => {
    setPage(1); // Reset to first page when debounce completes
  });
  const [view, setView] = useState<"grid" | "card">("grid");
  const [page, setPage] = useState(initialPage);
  const [functionalType, setFunctionalType] = useState<PipelineFunctionalType | null>(
    initialFunctionalType || null
  );
  const [selectedTags, setSelectedTags] = useState<string[]>(tags || []);

  const { data, loading } = useWorkspacePipelinesPageQuery({
    variables: {
      workspaceSlug: workspace.slug,
      search: debouncedSearchQuery,
      tags: selectedTags.length > 0 ? selectedTags : undefined,
      functionalType,
      page,
      perPage,
    },
  });

  const { data: allPipelinesData } = useWorkspacePipelinesPageQuery({
    variables: {
      workspaceSlug: workspace.slug,
      page: 1,
      perPage: 1000,
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

  const availableTags = React.useMemo(() => {
    const allItems = allPipelinesData?.pipelines?.items || [];
    if (!allItems.length) return [];
    const tagSet = new Set<string>();
    allItems.forEach((pipeline) => {
      pipeline.tags?.forEach((tag) => {
        tagSet.add(tag.name);
      });
    });
    return Array.from(tagSet).sort();
  }, [allPipelinesData]);

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
        tagsFilter={selectedTags}
        setTagsFilter={setSelectedTags}
        availableTags={availableTags}
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
