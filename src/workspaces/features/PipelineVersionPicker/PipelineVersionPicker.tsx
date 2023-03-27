import { gql } from "@apollo/client";
import Select from "core/components/forms/Select";
import { DateTime } from "luxon";
import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { PipelineVersionPicker_PipelineFragment } from "./PipelineVersionPicker.generated";

type Option = {
  id: string;
  number: number;
  createdAt: string;
  user?: { displayName: string } | null;
};

type PipelineVersionPickerProps = {
  value: Option | null;
  pipeline: PipelineVersionPicker_PipelineFragment;
  placeholder?: string;
  onChange(value: Option | null): void;
  required?: boolean;
};

const PipelineVersionPicker = (props: PipelineVersionPickerProps) => {
  const { pipeline, value, ...delegated } = props;
  const { t } = useTranslation();

  const getOptionLabel = useCallback(
    (option: Option) =>
      `V${option.number} - ${DateTime.fromISO(option.createdAt).toLocaleString(
        DateTime.DATETIME_MED
      )} - ${option.user?.displayName ?? t("Unknown")}`,
    [t]
  );
  const filterOptions = useCallback(
    (options: Option[], query: string) => {
      return options.filter((option) =>
        `V${option.number} - ${DateTime.fromISO(
          option.createdAt
        ).toLocaleString(DateTime.DATETIME_MED)} - ${
          option.user?.displayName ?? t("Unknown")
        }}`
          .toLowerCase()
          .includes(query.toLowerCase())
      );
    },
    [t]
  );

  return (
    <Select<Option>
      {...delegated}
      value={value}
      options={pipeline.versions.items ?? []}
      by="id"
      getOptionLabel={getOptionLabel}
      displayValue={getOptionLabel}
      filterOptions={filterOptions}
    />
  );
};

PipelineVersionPicker.fragments = {
  pipeline: gql`
    fragment PipelineVersionPicker_pipeline on Pipeline {
      id
      versions {
        items {
          id
          number
          createdAt
          parameters
          user {
            displayName
          }
        }
      }
    }
  `,
};

export default PipelineVersionPicker;
