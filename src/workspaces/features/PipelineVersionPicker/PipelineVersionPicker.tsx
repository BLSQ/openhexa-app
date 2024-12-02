import { gql, useLazyQuery } from "@apollo/client";
import { Combobox } from "core/components/forms/Combobox";
import useDebounce from "core/hooks/useDebounce";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import { useCallback, useMemo, useState } from "react";
import {
  PipelineVersionPickerQuery,
  PipelineVersionPicker_PipelineFragment,
  PipelineVersionPicker_VersionFragment,
} from "./PipelineVersionPicker.generated";

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
  const debouncedQuery = useDebounce(query, 150);
  const [fetch, { data, loading }] = useLazyQuery<PipelineVersionPickerQuery>(
    gql`
      query PipelineVersionPicker($pipelineId: UUID!) {
        pipeline(id: $pipelineId) {
          versions {
            items {
              ...PipelineVersionPicker_version
            }
          }
        }
      }
      ${PipelineVersionPicker.fragments.version}
    `,
  );

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
    () => filterOptions(data?.pipeline?.versions.items ?? [], debouncedQuery),
    [data, debouncedQuery, filterOptions],
  );

  const onOpen = useCallback(() => {
    fetch({ variables: { pipelineId: pipeline.id } });
  }, [fetch, pipeline.id]);

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
        code
        name
        help
        type
        default
        required
        choices
        multiple
      }
      user {
        displayName
      }
    }
  `,
};

export default PipelineVersionPicker;
