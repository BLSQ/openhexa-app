import React, { useEffect, useState } from "react";
import { useTranslation } from "next-i18next";
import { gql } from "@apollo/client";
import { toast } from "react-toastify";
import router from "next/router";
import useDebounce from "core/hooks/useDebounce";
import useCacheKey from "core/hooks/useCacheKey";
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

  const [createPipelineFromTemplateVersion] =
    useCreatePipelineFromTemplateVersionMutation();
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 300);
  const [tagsFilter, setTagsFilter] = useState<string[]>([]);
  const [functionalTypeFilter, setFunctionalTypeFilter] = useState<any>(null);
  const workspaceFilterOptions = [
    { id: 1, label: "All templates", workspaceSlug: "" },
    { id: 2, label: "From this workspace", workspaceSlug: workspace.slug },
  ];
  const [workspaceFilter, setWorkspaceFilter] = useState(
    workspaceFilterOptions[0],
  );

  const sourceFilterOptions = [
    { id: "all", label: "All sources", value: undefined },
    { id: "official", label: "Official", value: true },
    { id: "community", label: "Community", value: false },
  ];
  const [sourceFilter, setSourceFilter] = useState(sourceFilterOptions[0]);

  const { data, loading, error, refetch } = useGetPipelineTemplatesQuery({
    variables: {
      page,
      perPage,
      search: debouncedSearchQuery,
      currentWorkspaceSlug: workspace.slug,
      workspaceSlug: workspaceFilter.workspaceSlug ?? undefined,
      tags: tagsFilter.length > 0 ? tagsFilter : undefined,
      functionalType: functionalTypeFilter,
      isOfficial: sourceFilter.value,
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
        sourceFilter={sourceFilter}
        setSourceFilter={setSourceFilter}
        sourceFilterOptions={sourceFilterOptions}
      />
      <div className="relative">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center backdrop-blur-xs z-10">
            <Spinner />
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
    $isOfficial: Boolean
  ) {
    workspace(slug: $currentWorkspaceSlug) {
      pipelineTemplateTags
    }
    pipelineTemplates(
      page: $page
      perPage: $perPage
      search: $search
      workspaceSlug: $workspaceSlug
      tags: $tags
      functionalType: $functionalType
      isOfficial: $isOfficial
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
        isOfficial
        iconUrl
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
`;

PipelineTemplates.fragments = {
  workspace: gql`
    fragment PipelineTemplates_workspace on Workspace {
      slug
    }
  `,
};

export default PipelineTemplates;
