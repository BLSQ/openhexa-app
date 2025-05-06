import React, { useState, useRef, useEffect, useMemo } from "react";
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

const getTabLabel = (
  loading: boolean,
  label: string,
  totalItems?: number,
): string => {
  return loading ? label : `${label} (${totalItems || 0})`;
};

const pageSize = 15;

const SpotlightSearch = ({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) => {
  const { t } = useTranslation();
  const router = useRouter();

  const [unBouncedQuery, setUnBouncedQuery] = useState("");
  const query = useDebounce(unBouncedQuery, 500);
  const isBouncing = unBouncedQuery !== query;

  const [selectedWorkspaces, setSelectedWorkspaces] = useState<Workspace[]>([]);
  const selectedWorkspaceSlugs = useMemo(
    () => selectedWorkspaces?.map((workspace) => workspace.slug),
    [selectedWorkspaces],
  );

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
    datasetPage,
    pipelinePage,
    filePage,
    databaseTablePage,
    pipelineTemplatePage,
  ]);

  useEffect(() => {
    const handleRouteChange = () => {
      onClose();
    };

    router.events.on("routeChangeStart", handleRouteChange);

    return () => {
      router.events.off("routeChangeStart", handleRouteChange);
    };
  }, [router.events, onClose]);

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
  useOnClickOutside(searchBarRef, () => {
    if (isOpen) {
      onClose();
    }
  });

  const oneOfTheResultsLoading =
    isBouncing || tabConfigs.some(({ loading }) => loading);
  const showWorkspaceFilterPanel = unBouncedQuery;
  const showResults = unBouncedQuery;

  if (!isOpen) {
    return null;
  }
  return (
    <div
      className="fixed inset-0 z-50 bg-gray-900/70 flex justify-center"
      tabIndex={0}
    >
      <div className="flex w-2/3 mt-30" ref={searchBarRef}>
        <div className="relative">
          <div
            className={clsx(
              "transition-opacity duration-100 ease-in-out p-4 pb-8 bg-white rounded-t-lg min-h-45",
              showWorkspaceFilterPanel ? "opacity-100" : "opacity-0",
            )}
          >
            <WorkspaceFilterPanel
              workspaces={workspacesData?.workspaces?.items || []}
              selectedWorkspaces={selectedWorkspaces}
              onChange={setSelectedWorkspaces}
            />
          </div>
          <Input
            id="search-input"
            ref={inputRef}
            value={unBouncedQuery}
            data-testid="search-input"
            leading={<MagnifyingGlassIcon className="h-5 text-gray-500" />}
            autoComplete="off"
            trailingIcon={
              <button
                onClick={onClose}
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
            className={clsx(
              "w-full transition-all duration-100 ease-in-out",
              showWorkspaceFilterPanel && "rounded-t-none",
              showResults && "rounded-b-none",
            )}
            classNameOverrides={
              "focus:ring-0 focus:border-white border-white py-4"
            }
          />
          <div
            className={clsx(
              "transition-opacity duration-100 ease-in-out",
              showResults ? "opacity-100" : "opacity-0",
            )}
          >
            <div className="max-h-[400px] overflow-y-auto">
              <Tabs
                defaultIndex={0}
                className="bg-white p-3"
                onChange={handleTabChange}
              >
                <Tabs.Tab
                  label={`${t("All results")} (${numberOfResults}${oneOfTheResultsLoading ? "+" : ""})`}
                  className="bg-white rounded-b-md"
                >
                  <AllResultsTable
                    isActive={activeTabIndex === 0}
                    combinedResults={combinedResults}
                    highlightedIndex={highlightedIndex}
                    hasPreviousPage={hasPreviousPageOverall}
                    hasNextPage={hasNextPageOverall}
                    fetchNextPage={fetchNextPage}
                    fetchPreviousPage={fetchPreviousPage}
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
                      leadingElement={React.createElement(
                        getTypeIcon(typeName),
                        {
                          className: "h-5 text-gray-500",
                        },
                      )}
                      label={getTabLabel(loading, label, data?.totalItems)}
                      className="bg-white rounded-b-md"
                      loading={isBouncing || loading}
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
    query SearchPipelines($query: String!, $workspaceSlugs: [String]!, $page: Int, $perPage: Int) {
      pipelines: searchPipelines(query: $query, workspaceSlugs: $workspaceSlugs, page: $page, perPage: $perPage) {
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
    query GetWorkspaces($page: Int, $perPage: Int) {
      workspaces(page: $page, perPage: $perPage) {
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

export default SpotlightSearch;
