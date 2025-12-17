import React, { useEffect, useState } from "react";
import { useTranslation } from "next-i18next";
import { gql } from "@apollo/client";
import useDebounce from "core/hooks/useDebounce";
import useCacheKey from "core/hooks/useCacheKey";
import { getCookie, hasCookie, setCookie } from "cookies-next";
import {
  getTemplateSortOptions,
  templateSorting,
  TemplateSortOption,
} from "pipelines/config/sorting";
import { SortingRule } from "react-table";
import {
  PipelineTemplates_WorkspaceFragment,
  useGetPipelineTemplatesQuery,
} from "./PipelineTemplates.generated";
import CardView from "./CardView";
import GridView from "./GridView";
import Header from "./Header";
import Spinner from "core/components/Spinner";
import User from "core/features/User";

export let cookiePipelineTemplatesView: "grid" | "card" = "grid";

function getDefaultPipelineTemplatesView(): "grid" | "card" {
  if (typeof window === "undefined") {
    return cookiePipelineTemplatesView;
  } else if (hasCookie("pipeline-templates-view")) {
    return getCookie("pipeline-templates-view") as "grid" | "card";
  } else {
    return "grid";
  }
}

type PipelineTemplatesProps = {
  workspace: PipelineTemplates_WorkspaceFragment;
  showCard?: boolean;
};

const PipelineTemplates = ({
  workspace,
  showCard = true,
}: PipelineTemplatesProps) => {
  const { t } = useTranslation();
  const [view, setView] = useState<"grid" | "card">(
    getDefaultPipelineTemplatesView(),
  );
  const [page, setPage] = useState(1);

  const handleSetView = (newView: "grid" | "card") => {
    setView(newView);
    setCookie("pipeline-templates-view", newView, {
      maxAge: 60 * 60 * 24 * 365,
    });
  };
  const perPage = 10;

  const sortOptions = getTemplateSortOptions();
  const [sortOrder, setSortOrder] = useState<TemplateSortOption>(
    sortOptions[0],
  );

  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 300);
  const [tagsFilter, setTagsFilter] = useState<string[]>([]);
  const [functionalTypeFilter, setFunctionalTypeFilter] = useState<any>(null);
  const [validationFilter, setValidationFilter] = useState<boolean | null>(
    null,
  );
  const workspaceFilterOptions = [
    { id: 1, label: "All templates", workspaceSlug: "" },
    { id: 2, label: "From this workspace", workspaceSlug: workspace.slug },
  ];
  const [workspaceFilter, setWorkspaceFilter] = useState(
    workspaceFilterOptions[0],
  );

  const { data, loading, error, refetch } = useGetPipelineTemplatesQuery({
    variables: {
      page,
      perPage,
      search: debouncedSearchQuery,
      currentWorkspaceSlug: workspace.slug,
      workspaceSlug: workspaceFilter.workspaceSlug ?? undefined,
      tags: tagsFilter.length > 0 ? tagsFilter : undefined,
      functionalType: functionalTypeFilter,
      isValidated: validationFilter,
      orderBy: sortOrder.orderBy,
    },
    fetchPolicy: "cache-and-network", // The template list is a global list across the instance, so we want to check the network for updates and show the cached data in the meantime
  });
  const [items, setItems] = useState(data?.pipelineTemplates?.items || []);

  useEffect(() => {
    if (!loading && data?.pipelineTemplates?.items) {
      setItems(data.pipelineTemplates.items);
    }
  }, [loading, data]);

  useCacheKey("templates", () => refetch());

  const totalItems = data?.pipelineTemplates?.totalItems ?? 0;
  const templateTags = data?.workspace?.pipelineTemplateTags || [];

  if (error) return <p>{t("Error loading templates")}</p>;

  const handleDataGridSort = (params: {
    page: number;
    pageSize: number;
    pageIndex: number;
    sortBy: SortingRule<object>[];
  }) => {
    const orderBy = templateSorting.convertDataGridSort(params.sortBy);
    if (orderBy) {
      const matchingOption = sortOptions.find((opt) => opt.orderBy === orderBy);
      if (matchingOption) {
        setSortOrder(matchingOption);
      }
    }
    setPage(params.page);
  };

  const ViewTemplates = view === "card" ? CardView : GridView;
  return (
    <div>
      <Header
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        filter={{ workspaceFilter, setWorkspaceFilter, workspaceFilterOptions }}
        view={view}
        setView={handleSetView}
        showCard={showCard}
        tagsFilter={tagsFilter}
        setTagsFilter={setTagsFilter}
        templateTags={templateTags}
        functionalTypeFilter={functionalTypeFilter}
        setFunctionalTypeFilter={setFunctionalTypeFilter}
        validationFilter={validationFilter}
        setValidationFilter={setValidationFilter}
        sortOrder={sortOrder}
        setSortOrder={setSortOrder}
        sortOptions={sortOptions}
      />
      <div className="relative">
        {loading && (
          <div className="absolute inset-0 z-10 flex items-center justify-center bg-white bg-opacity-60">
            <Spinner size="md" />
          </div>
        )}
        <ViewTemplates
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

const GET_PIPELINE_TEMPLATES = gql`
  query GetPipelineTemplates(
    $page: Int!
    $perPage: Int!
    $search: String
    $currentWorkspaceSlug: String!
    $workspaceSlug: String
    $tags: [String!]
    $functionalType: PipelineFunctionalType
    $isValidated: Boolean
    $orderBy: PipelineTemplateOrderBy
  ) {
    workspace(slug: $currentWorkspaceSlug) {
      slug
      pipelineTemplateTags
    }
    pipelineTemplates(
      page: $page
      perPage: $perPage
      search: $search
      workspaceSlug: $workspaceSlug
      tags: $tags
      functionalType: $functionalType
      isValidated: $isValidated
      orderBy: $orderBy
    ) {
      pageNumber
      totalPages
      totalItems
      items {
        id
        description
        code
        name
        functionalType
        validatedAt
        pipelinesCount
        tags {
          id
          name
        }
        workspace {
          slug
          name
        }
        organization {
          name
          logo
        }
        currentVersion {
          id
          versionNumber
          createdAt
          user {
            ...User_user
          }
          template {
            sourcePipeline {
              name
            }
          }
        }
      }
    }
  }
  ${User.fragments.user}
`;

PipelineTemplates.fragments = {
  workspace: gql`
    fragment PipelineTemplates_workspace on Workspace {
      slug
    }
  `,
};

PipelineTemplates.prefetch = async (ctx: any) => {
  // Load the cookie value from the request to render it correctly on the server
  cookiePipelineTemplatesView = (await hasCookie(
    "pipeline-templates-view",
    ctx,
  ))
    ? ((await getCookie("pipeline-templates-view", ctx)) as "grid" | "card")
    : "grid";
};

export default PipelineTemplates;
