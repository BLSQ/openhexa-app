import { gql, useQuery } from "@apollo/client";
import Listbox from "core/components/Listbox/Listbox";
import {
  DatasetVersionPicker_DatasetFragment,
  DatasetVersionPicker_VersionFragment,
} from "./DatasetVersionPicker.generated";
import { DateTime } from "luxon";
import { useState } from "react";

type DatasetVersionPickerProps = {
  onChange(version: any | null): void;
  version: DatasetVersionPicker_VersionFragment | null;
  dataset: DatasetVersionPicker_DatasetFragment;
  className?: string;
};

const DatasetVersionPicker = (props: DatasetVersionPickerProps) => {
  const { onChange, dataset, version, className } = props;
  const [perPage, setPerPage] = useState(10);
  const { data, previousData, loading } = useQuery(
    gql`
      query DatasetVersionPicker($datasetId: ID!, $perPage: Int!) {
        dataset(id: $datasetId) {
          versions(perPage: $perPage) {
            totalItems
            items {
              ...DatasetVersionPicker_version
            }
          }
        }
      }

      ${DatasetVersionPicker.fragments.version}
    `,
    { variables: { datasetId: dataset.id, perPage } },
  );

  const versions = (data ?? previousData)?.dataset.versions ?? {
    items: [],
    totalItems: 0,
  };

  const getOptionLabel = (item: DatasetVersionPicker_VersionFragment) => {
    let res = [];
    if (item?.name) {
      res.push(item.name);
    }
    if (item?.createdAt) {
      res.push(DateTime.fromISO(item.createdAt).toLocaleString());
    }
    return res.join(" - ");
  };

  const onScrollBottom = () => {
    if (versions.totalItems > versions.items.length && !loading) {
      setPerPage(perPage + 10);
    }
  };

  return (
    <Listbox
      value={version}
      className={className}
      onChange={onChange}
      options={versions.items}
      by="id"
      onScrollBottom={onScrollBottom}
      getOptionLabel={getOptionLabel}
    />
  );
};

DatasetVersionPicker.fragments = {
  version: gql`
    fragment DatasetVersionPicker_version on DatasetVersion {
      id
      name
      createdAt
    }
  `,
  dataset: gql`
    fragment DatasetVersionPicker_dataset on Dataset {
      id
    }
  `,
};

export default DatasetVersionPicker;
