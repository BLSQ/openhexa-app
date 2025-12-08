import React, { useState, useRef, useEffect, useMemo } from "react";
import { createPortal } from "react-dom";
import clsx from "clsx";
import { MagnifyingGlassIcon, XMarkIcon } from "@heroicons/react/24/outline";
import Input from "core/components/forms/Input";
import { useTranslation } from "next-i18next";
import { gql } from "@apollo/client";
import useDebounce from "core/hooks/useDebounce";
import {
  useSearchDatabaseTablesLazyQuery,
  useSearchDatasetsLazyQuery,
  useSearchPipelinesLazyQuery,
  useSearchPipelineTemplatesLazyQuery,
  GetWorkspacesQuery,
  useSearchFilesLazyQuery,
  useGetWorkspacesLazyQuery,
} from "./SpotlightSearch.generated";
import DatasetResultTable from "./DatasetResultTable";
import PipelineResultTable from "./PipelineResultTable";
import DatabaseTableResultTable from "./DatabaseTableResultTable";
import PipelineTemplateResultTable from "./PipelineTemplateResultTable";
import AllResultsTable from "./AllResultsTable";
import useSearchHotkeys from "./useSearchHotkeys";
import Tabs from "core/components/Tabs";
import {
  getItems,
  getTotalItems,
  getTypeIcon,
  hasNextPage,
  hasPreviousPage,
  TypeName,
} from "./mapper";
import { useRouter } from "next/router";
import WorkspaceDisplay from "./WorkspaceDisplay";
import WorkspaceFilterPanel from "./WorkspaceFilterPanel";
import FileResultTable from "./FileResultTable";
import useOnClickOutside from "use-onclickoutside";
import { max } from "lodash";
import InputSearch from "./InputSearch";
import Spinner from "core/components/Spinner";
import { GetServerSidePropsContext } from "next";
import { PipelineFunctionalType } from "graphql/types";
import { formatPipelineFunctionalType } from "workspaces/helpers/pipelines";
import Select from "core/components/forms/Select";

type Workspace = GetWorkspacesQuery["workspaces"]["items"][0];

type TabConfig = {
  typeName: TypeName;
  loading: boolean;
  data: any;
  label: string;
  Component: React.ComponentType<any>;
  propsKey: string;
  setPage: React.Dispatch<React.SetStateAction<number>>;
};

const ALL_FUNCTIONAL_TYPES = null;

const getTabLabel = (label: string, totalItems?: number): string => {
  return `${label} (${totalItems || 0})`;
};

const pageSize = 15;

const SpotlightSearch = ({ organizationId }: { organizationId?: string }) => {
  const { t } = useTranslation();
  const router = useRouter();

  const [isOpen, setIsOpen] = useState(false);
  const [unBouncedQuery, setUnBouncedQuery] = useState("");
  const query = useDebounce(unBouncedQuery, 500);

  const [selectedWorkspaces, setSelectedWorkspaces] = useState<Workspace[]>([]);
  const selectedWorkspaceSlugs = useMemo(
    () => selectedWorkspaces?.map((workspace) => workspace.slug),
    [selectedWorkspaces],
  );
  const [functionalTypeFilter, setFunctionalTypeFilter] =
    useState<PipelineFunctionalType | null>(ALL_FUNCTIONAL_TYPES);

  const inputRef = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

  const [searchWorkspaces, { data: workspacesData }] =
    useGetWorkspacesLazyQuery();

  useEffect(() => {
    if (isOpen) {
      searchWorkspaces({
        variables: {
          organizationId,
          perPage: 1000,
        },
      }).then();
    }
  }, [isOpen]);

  useEffect(() => {
    if (workspacesData?.workspaces?.items) {
      setSelectedWorkspaces(
        workspacesData.workspaces.items, // Select all workspaces by default
      );
    }
  }, [workspacesData]);

  const [datasetPage, setDatasetPage] = useState(1);
  const [pipelinePage, setPipelinePage] = useState(1);
  const [filePage, setFilePage] = useState(1);
  const [databaseTablePage, setDatabaseTablePage] = useState(1);
  const [pipelineTemplatePage, setPipelineTemplatePage] = useState(1);

  const [searchDatasets, { data: datasetsData, loading: datasetsLoading }] =
    useSearchDatasetsLazyQuery();
  const [searchPipelines, { data: pipelinesData, loading: pipelinesLoading }] =
    useSearchPipelinesLazyQuery();
  const [
    searchPipelineTemplates,
    { data: pipelineTemplatesData, loading: pipelineTemplatesLoading },
  ] = useSearchPipelineTemplatesLazyQuery();
  const [
    searchDatabaseTables,
    { data: databaseTablesData, loading: databaseTablesLoading },
  ] = useSearchDatabaseTablesLazyQuery();
  const [searchFiles, { data: filesData, loading: filesLoading }] =
    useSearchFilesLazyQuery();

  useEffect(() => {
    if (isOpen && query) {
      setHighlightedIndex(0);
      searchDatasets({
        variables: {
          query,
          workspaceSlugs: selectedWorkspaceSlugs,
          page: datasetPage,
          perPage: pageSize,
        },
      }).then();
      searchPipelines({
        variables: {
          query,
          workspaceSlugs: selectedWorkspaceSlugs,
          page: pipelinePage,
          perPage: pageSize,
          functionalType: functionalTypeFilter,
        },
      }).then();
      searchPipelineTemplates({
        variables: {
          query,
          workspaceSlugs: selectedWorkspaceSlugs,
          page: pipelineTemplatePage,
          perPage: pageSize,
        },
      }).then();
      searchDatabaseTables({
        variables: {
          query,
          workspaceSlugs: selectedWorkspaceSlugs,
          page: databaseTablePage,
          perPage: pageSize,
        },
      }).then();
      searchFiles({
        variables: {
          query,
          workspaceSlugs: selectedWorkspaceSlugs,
          page: filePage,
          perPage: pageSize,
        },
      }).then();
    }
  }, [
    isOpen,
    query,
    selectedWorkspaceSlugs,
    functionalTypeFilter,
    datasetPage,
    pipelinePage,
    filePage,
    databaseTablePage,
    pipelineTemplatePage,
  ]);

  useEffect(() => {
    const handleRouteChange = () => {
      setIsOpen(false);
      setUnBouncedQuery("");
      setHighlightedIndex(0);
    };

    router.events.on("routeChangeStart", handleRouteChange);

    return () => {
      router.events.off("routeChangeStart", handleRouteChange);
    };
  }, [router.events]);

  const [activeTabIndex, setActiveTabIndex] = useState(0);
  const [highlightedIndex, setHighlightedIndex] = useState(0);

  const handleTabChange = (index: number) => {
    setActiveTabIndex(index);
    setHighlightedIndex(0);
  };

  const tabConfigs: TabConfig[] = [
    {
      typeName: "DatasetResult",
      loading: datasetsLoading,
      data: datasetsData?.datasets,
      label: t("Datasets"),
      Component: DatasetResultTable,
      propsKey: "datasetsPage",
      setPage: setDatasetPage,
    },
    {
      typeName: "DatabaseTableResult",
      loading: databaseTablesLoading,
      data: databaseTablesData?.databaseTables,
      label: t("Tables"),
      Component: DatabaseTableResultTable,
      propsKey: "databaseTablesPage",
      setPage: setDatabaseTablePage,
    },
    {
      typeName: "FileResult",
      loading: filesLoading,
      data: filesData?.files,
      label: t("Files"),
      Component: FileResultTable,
      propsKey: "filesPage",
      setPage: setFilePage,
    },
    {
      typeName: "PipelineResult",
      loading: pipelinesLoading,
      data: pipelinesData?.pipelines,
      label: t("Pipelines"),
      Component: PipelineResultTable,
      propsKey: "pipelinesPage",
      setPage: setPipelinePage,
    },
    {
      typeName: "PipelineTemplateResult",
      loading: pipelineTemplatesLoading,
      data: pipelineTemplatesData?.pipelineTemplates,
      label: t("Templates"),
      Component: PipelineTemplateResultTable,
      propsKey: "pipelineTemplatesPage",
      setPage: setPipelineTemplatePage,
    },
  ];

  const {
    combinedResults,
    numberOfResults,
    hasNextPageOverall,
    hasPreviousPageOverall,
  } = useMemo(() => {
    const allData = tabConfigs.map((tab) => tab.data);

    const currentPageNumber = max(allData.map((data) => data?.pageNumber));

    const combinedResults = allData
      .filter((data) => data?.pageNumber === currentPageNumber)
      .flatMap(getItems)
      .sort((a, b) => b.score - a.score);

    const numberOfResults = allData.reduce(
      (total, data) => total + getTotalItems(data),
      0,
    );

    const hasNextPageOverall = allData.some(hasNextPage);
    const hasPreviousPageOverall = allData.some(hasPreviousPage);

    return {
      combinedResults,
      numberOfResults,
      hasNextPageOverall,
      hasPreviousPageOverall,
    };
  }, [
    datasetsData,
    pipelinesData,
    pipelineTemplatesData,
    databaseTablesData,
    filesData,
  ]);

  const currentData =
    activeTabIndex == 0
      ? combinedResults
      : tabConfigs[activeTabIndex - 1]?.data?.items || [];

  useSearchHotkeys({
    isOpen,
    setIsOpen,
    inputRef,
    data: currentData,
    highlightedIndex,
    setHighlightedIndex: (updateFn) => {
      setHighlightedIndex((prev) => {
        const newIndex = updateFn(prev);
        return Math.max(0, Math.min(currentData.length - 1, newIndex));
      });
    },
  });

  const resetPages = () => {
    tabConfigs.forEach(({ setPage }) => setPage(1));
  };

  const fetchNextPage = () =>
    tabConfigs.forEach(({ data, setPage }) => {
      if (hasNextPage(data)) {
        setPage((prev) => prev + 1);
      }
    });
  const fetchPreviousPage = () =>
    tabConfigs.forEach(({ data, setPage }) => {
      if (hasPreviousPage(data)) {
        setPage((prev) => prev - 1);
      }
    });

  const searchBarRef = useRef<HTMLDivElement>(null);
  useOnClickOutside(searchBarRef, () => setIsOpen(false));

  const showResults = unBouncedQuery && query === unBouncedQuery;

  const overlay = (
    <div
      className="fixed inset-0 z-50 bg-gray-900/70 flex justify-center backdrop-blur-xs"
      tabIndex={0}
    >
      <div className="flex w-2/3 mt-30">
        <div className="relative">
          <div ref={searchBarRef}>
            <Input
              id="search-input"
              ref={inputRef}
              value={unBouncedQuery}
              data-testid="search-input"
              leading={<MagnifyingGlassIcon className="h-5 text-gray-500" />}
              autoComplete="off"
              trailingIcon={
                <button
                  onClick={() => setIsOpen(false)}
                  className="flex items-center text-gray-500 hover:text-gray-700 focus:text-gray-700"
                  aria-label="Close"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              }
              placeholder={t(
                "Search for files, pipelines, templates, database, datasets,...",
              )}
              onChange={(event) => {
                resetPages();
                setUnBouncedQuery(event.target.value ?? "");
              }}
              className={clsx("w-full", showResults && "rounded-b-none")}
              classNameOverrides={
                "focus:ring-0 focus:border-white border-white py-4"
              }
            />
            <div onClick={showResults ? undefined : () => setIsOpen(false)}>
              <div
                className={clsx(
                  "transition-opacity duration-100 ease-in-out",
                  showResults ? "opacity-100 visible" : "opacity-0 invisible",
                )}
                data-testid="spotlight-search-results-panel"
              >
                <WorkspaceFilterPanel
                  workspaces={workspacesData?.workspaces?.items || []}
                  selectedWorkspaces={selectedWorkspaces}
                  onChange={setSelectedWorkspaces}
                />
                <div className="bg-white p-4 border-t border-gray-200">
                  <p className="text-md font-medium mb-3">
                    {t("Filter by Functional Type")}
                  </p>
                  <Select
                    options={[
                      ALL_FUNCTIONAL_TYPES,
                      ...Object.values(PipelineFunctionalType),
                    ]}
                    value={functionalTypeFilter}
                    onChange={(value) =>
                      setFunctionalTypeFilter(
                        value as PipelineFunctionalType | null,
                      )
                    }
                    getOptionLabel={(option) =>
                      option
                        ? formatPipelineFunctionalType(option)
                        : t("All types")
                    }
                    displayValue={(option) =>
                      option
                        ? formatPipelineFunctionalType(option)
                        : t("All types")
                    }
                    className="w-full"
                  />
                </div>
                <Tabs
                  defaultIndex={0}
                  className="bg-white p-3 border-none"
                  onChange={handleTabChange}
                >
                  <Tabs.Tab
                    label={getTabLabel(t("All results"), numberOfResults)}
                    className="bg-white rounded-b-md max-h-[50vh] overflow-y-auto"
                  >
                    <AllResultsTable
                      isActive={activeTabIndex === 0}
                      combinedResults={combinedResults}
                      highlightedIndex={highlightedIndex}
                      hasPreviousPage={hasPreviousPageOverall}
                      hasNextPage={hasNextPageOverall}
                      fetchNextPage={fetchNextPage}
                      fetchPreviousPage={fetchPreviousPage}
                      pageSize={pageSize * tabConfigs.length}
                    />
                  </Tabs.Tab>
                  {tabConfigs.map(
                    (
                      {
                        Component,
                        typeName,
                        loading,
                        propsKey,
                        label,
                        data,
                        setPage,
                      },
                      index,
                    ) => (
                      <Tabs.Tab
                        key={index}
                        leadingElement={
                          loading ? (
                            <Spinner
                              size="xs"
                              className="h-4 w-4 text-pink-500"
                            />
                          ) : (
                            React.createElement(getTypeIcon(typeName), {
                              className: "h-4 w-4 text-gray-500",
                            })
                          )
                        }
                        label={getTabLabel(label, data?.totalItems)}
                        className="bg-white rounded-b-md max-h-[50vh] overflow-y-auto"
                      >
                        <Component
                          {...{ [propsKey]: data }}
                          isActive={activeTabIndex === index + 1}
                          highlightedIndex={highlightedIndex}
                          fetchData={(params: { page: number }) =>
                            setPage(params.page)
                          }
                          setPage={setPage}
                          pageSize={pageSize}
                        />
                      </Tabs.Tab>
                    ),
                  )}
                </Tabs>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <>
      <InputSearch onClick={() => setIsOpen((prev) => !prev)} />
      {typeof window !== "undefined" &&
        isOpen &&
        createPortal(overlay, document.body)}
    </>
  );
};

SpotlightSearch.fragments = {
  datasets: gql`
    query SearchDatasets($query: String!, $workspaceSlugs: [String]!, $page: Int, $perPage: Int) {
      datasets: searchDatasets(query: $query, workspaceSlugs: $workspaceSlugs, page: $page, perPage: $perPage) {
        __typename
        ...DatasetsPage
      }
      ${DatasetResultTable.fragments.datasetsPage}
    }
  `,
  pipelines: gql`
    query SearchPipelines($query: String!, $workspaceSlugs: [String]!, $page: Int, $perPage: Int, $functionalType: PipelineFunctionalType) {
      pipelines: searchPipelines(query: $query, workspaceSlugs: $workspaceSlugs, page: $page, perPage: $perPage, functionalType: $functionalType) {
        __typename
        ...PipelinesPage
      }
      ${PipelineResultTable.fragments.pipelinesPage}
    }
  `,
  pipelineTemplates: gql`
    query SearchPipelineTemplates($query: String!, $workspaceSlugs: [String]!, $page: Int, $perPage: Int) {
      pipelineTemplates: searchPipelineTemplates(
        query: $query
        workspaceSlugs: $workspaceSlugs
          page: $page
          perPage: $perPage
      ) {
        __typename
        ...PipelineTemplatesPage
      }
      ${PipelineTemplateResultTable.fragments.pipelineTemplatesPage}
    }
  `,
  databaseTables: gql`
    query SearchDatabaseTables($query: String!, $workspaceSlugs: [String]!, $page: Int, $perPage: Int) {
      databaseTables: searchDatabaseTables(
        query: $query
        workspaceSlugs: $workspaceSlugs
          page: $page
          perPage: $perPage
      ) {
        __typename
        ...DatabaseTablesPage
      }
      ${DatabaseTableResultTable.fragments.databaseTablesPage}
    }
  `,
  files: gql`
    query SearchFiles($query: String!, $workspaceSlugs: [String]!, $page: Int, $perPage: Int) {
      files: searchFiles(query: $query, workspaceSlugs: $workspaceSlugs, page: $page, perPage: $perPage) {
        __typename
        ...FilesPage
      }
      ${FileResultTable.fragments.filesPage}
    }
  `,
  workspaces: gql`
    query GetWorkspaces($organizationId: UUID, $page: Int, $perPage: Int) {
      workspaces(organizationId: $organizationId, page: $page, perPage: $perPage) {
        totalItems
        items {
          slug
          ...WorkspaceDisplayFragment
        }
      }
      ${WorkspaceDisplay.fragments.workspace}
    }
  `,
};

SpotlightSearch.prefetch = async (ctx: GetServerSidePropsContext) => {
  await InputSearch.prefetch(ctx);
};

export default SpotlightSearch;
