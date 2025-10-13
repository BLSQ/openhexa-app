import { gql } from "@apollo/client";
import { Combobox } from "core/components/forms/Combobox";
import useDebounce from "core/hooks/useDebounce";
import useCacheKey from "core/hooks/useCacheKey";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import { useCallback, useMemo, useState, useEffect } from "react";
import {
  PipelineVersionPicker_PipelineFragment,
  PipelineVersionPicker_VersionFragment,
} from "./PipelineVersionPicker.generated";
import { usePipelineVersionPickerLazyQuery } from "workspaces/graphql/queries.generated";

type Option = {
  id: string;
  versionName: string;
  createdAt: string;
  user?: { displayName: string } | null;
};

type PipelineVersionPickerProps = {
  value: Option | null;
  pipeline: PipelineVersionPicker_PipelineFragment;
  placeholder?: string;
  onChange(value: PipelineVersionPicker_VersionFragment | null): void;
  required?: boolean;
  disabled?: boolean;
};

const PipelineVersionPicker = (props: PipelineVersionPickerProps) => {
  const { pipeline, value, ...delegated } = props;
  const { t } = useTranslation();
  const [query, setQuery] = useState("");
  const [allVersions, setAllVersions] = useState<Option[]>([]);
  const debouncedQuery = useDebounce(query, 150);
  const [fetch, { data, loading, refetch }] =
    usePipelineVersionPickerLazyQuery();
  useEffect(() => {
    if (data?.pipeline?.versions.items) {
      if (data.pipeline.versions.pageNumber === 1) {
        setAllVersions(data.pipeline.versions.items);
      } else {
        setAllVersions((prev) => [
          ...prev,
          ...(data.pipeline?.versions.items || []),
        ]);
      }
    }
  }, [data]);

  useCacheKey(["pipeline", pipeline.id], () => {
    setAllVersions([]);
    if (data) {
      refetch({ page: 1, perPage: 20 }).then();
    } else {
      fetch({
        variables: { pipelineId: pipeline.id, page: 1, perPage: 20 },
      }).then();
    }
  });

  const displayValue = useCallback(
    (option: Option) =>
      option
        ? `${option.versionName} - ${DateTime.fromISO(
            option.createdAt,
          ).toLocaleString(DateTime.DATETIME_MED)}`
        : "",
    [],
  );
  const filterOptions = useCallback(
    (options: Option[], query: string) => {
      return options.filter((option) =>
        `V${option.versionName} - ${DateTime.fromISO(
          option.createdAt,
        ).toLocaleString(
          DateTime.DATETIME_MED,
        )} - ${option.user?.displayName ?? t("Unknown")}}`
          .toLowerCase()
          .includes(query.toLowerCase()),
      );
    },
    [t],
  );

  const filteredVersions = useMemo(
    () => filterOptions(allVersions, debouncedQuery),
    [allVersions, debouncedQuery, filterOptions],
  );

  const onOpen = useCallback(() => {
    if (allVersions.length === 0) {
      fetch({
        variables: { pipelineId: pipeline.id, page: 1, perPage: 20 },
      }).then();
    }
  }, [fetch, pipeline.id, allVersions.length]);

  const loadMore = useCallback(() => {
    if (!loading && data?.pipeline?.versions) {
      const nextPage = (data.pipeline.versions.pageNumber || 0) + 1;
      fetch({
        variables: {
          pipelineId: pipeline.id,
          page: nextPage,
          perPage: 20,
        },
      }).then();
    }
  }, [loading, data, fetch, pipeline.id]);

  const hasMorePages =
    data?.pipeline?.versions &&
    data.pipeline.versions.pageNumber < data.pipeline.versions.totalPages;

  return (
    <Combobox
      {...delegated}
      value={value}
      by="id"
      loading={loading}
      onOpen={onOpen}
      placeholder={t("Select a version")}
      displayValue={displayValue}
      onInputChange={useCallback((event) => setQuery(event.target.value), [])}
      onClose={useCallback(() => setQuery(""), [])}
      withPortal
    >
      {filteredVersions.map((version) => (
        <Combobox.CheckOption value={version} key={version.id}>
          {displayValue(version)}
        </Combobox.CheckOption>
      ))}
      {hasMorePages && (
        <div className="px-3 py-2 border-t">
          <button
            onClick={loadMore}
            disabled={loading}
            className="w-full text-sm text-blue-600 hover:text-blue-800 disabled:text-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? t("Loading...") : t("Load more versions")}
          </button>
        </div>
      )}
    </Combobox>
  );
};

PipelineVersionPicker.fragments = {
  pipeline: gql`
    fragment PipelineVersionPicker_pipeline on Pipeline {
      id
    }
  `,
  version: gql`
    fragment PipelineVersionPicker_version on PipelineVersion {
      id
      versionName
      createdAt
      config
      parameters {
        ...ParameterField_parameter
      }
      user {
        displayName
      }
    }
  `,
};

export default PipelineVersionPicker;
