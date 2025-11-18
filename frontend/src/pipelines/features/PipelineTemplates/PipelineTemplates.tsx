import React, { useEffect, useState } from "react";
import { useTranslation } from "next-i18next";
import { gql } from "@apollo/client";
import { toast } from "react-toastify";
import router from "next/router";
import useDebounce from "core/hooks/useDebounce";
import useCacheKey from "core/hooks/useCacheKey";
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
import { useCreatePipelineFromTemplateVersionMutation } from "pipelines/graphql/mutations.generated";
import { CreatePipelineFromTemplateVersionError } from "graphql/types";
import CardView from "./CardView";
import GridView from "./GridView";
import Header from "./Header";
import Spinner from "core/components/Spinner";
import User from "core/features/User";

type PipelineTemplatesProps = {
  workspace: PipelineTemplates_WorkspaceFragment;
  showCard?: boolean;
};

const PipelineTemplates = ({
  workspace,
  showCard = true,
}: PipelineTemplatesProps) => {
  const { t } = useTranslation();
  const [view, setView] = useState<"grid" | "card">("grid");
  const [page, setPage] = useState(1);
  const perPage = 10;
  const clearCache = useCacheKey(["pipelines"]);

  const sortOptions = getTemplateSortOptions();
  const [sortOrder, setSortOrder] = useState<TemplateSortOption>(sortOptions[0]);

  const [createPipelineFromTemplateVersion] =
    useCreatePipelineFromTemplateVersionMutation();
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 300);
  const [tagsFilter, setTagsFilter] = useState<string[]>([]);
  const [functionalTypeFilter, setFunctionalTypeFilter] = useState<any>(null);
  const [publisherFilter, setPublisherFilter] = useState<string | null>(null);
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
      publisher: publisherFilter ?? undefined,
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

  // Extract unique publishers from all loaded templates
  const availablePublishers: string[] = React.useMemo(() => {
    if (!data?.pipelineTemplates?.items) return [];
    const publishers = data.pipelineTemplates.items
      .map((item: any) => item.publisher)
      .filter((publisher: any): publisher is string => !!publisher);
    return Array.from(new Set(publishers)).sort();
  }, [data?.pipelineTemplates?.items]);

  if (error) return <p>{t("Error loading templates")}</p>;

  const createPipeline = (pipelineTemplateVersionId: string) => () => {
    createPipelineFromTemplateVersion({
      variables: {
        input: {
          pipelineTemplateVersionId: pipelineTemplateVersionId,
          workspaceSlug: workspace.slug,
        },
      },
    })
      .then((result) => {
        const success = result.data?.createPipelineFromTemplateVersion?.success;
        const errors = result.data?.createPipelineFromTemplateVersion?.errors;
        const pipeline =
          result.data?.createPipelineFromTemplateVersion?.pipeline;
        if (success && pipeline) {
          clearCache();
          toast.success(
            t("Successfully created pipeline {{pipelineName}}", {
              pipelineName: pipeline.name,
            }),
          );
          router
            .push(
              `/workspaces/${encodeURIComponent(
                workspace.slug,
              )}/pipelines/${encodeURIComponent(pipeline.code)}`,
            )
            .then();
        } else if (
          errors?.includes(
            CreatePipelineFromTemplateVersionError.PermissionDenied,
          )
        ) {
          toast.error(t("You are not allowed to create a pipeline."));
        } else {
          toast.error(t("Unknown error : Failed to create pipeline"));
        }
      })
      .catch(() => {
        toast.error(t("Failed to create pipeline"));
      });
  };

  const handleDataGridSort = (params: {
    page: number;
    pageSize: number;
    pageIndex: number;
    sortBy: SortingRule<object>[];
  }) => {
    const orderBy = templateSorting.convertDataGridSort(params.sortBy);
    if (orderBy) {
      const matchingOption = sortOptions.find(
        opt => opt.orderBy === orderBy
      );
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
        setView={setView}
        showCard={showCard}
        tagsFilter={tagsFilter}
        setTagsFilter={setTagsFilter}
        templateTags={templateTags}
        functionalTypeFilter={functionalTypeFilter}
        setFunctionalTypeFilter={setFunctionalTypeFilter}
        publisherFilter={publisherFilter}
        setPublisherFilter={setPublisherFilter}
        availablePublishers={availablePublishers}
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
          createPipeline={createPipeline}
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
    $publisher: String
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
      publisher: $publisher
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
        publisher
        validatedAt
        pipelinesCount
        tags {
          id
          name
        }
        permissions {
          delete
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

export default PipelineTemplates;
