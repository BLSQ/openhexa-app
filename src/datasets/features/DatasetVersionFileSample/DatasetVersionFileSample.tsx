import { gql, useQuery } from "@apollo/client";
import Spinner from "core/components/Spinner";
import { ApolloComponent } from "core/helpers/types";
import { useTranslation } from "react-i18next";
import { DatasetVersionFileSample_FileFragment } from "./DatasetVersionFileSample.generated";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import { useMemo } from "react";
import DescriptionList from "core/components/DescriptionList";

interface DatasetVersionFileSampleProps {
  file: DatasetVersionFileSample_FileFragment;
}

const GET_DATASET_VERSION_FILE_SAMPLE = gql`
  query GetDatasetVersionFileSample($id: ID!) {
    datasetVersionFile(id: $id) {
      id
      properties
      fileSample {
        sample
        status
        statusReason
      }
    }
  }
`;

export const DatasetVersionFileSample: ApolloComponent<
  DatasetVersionFileSampleProps
> = (props) => {
  const { t } = useTranslation();
  const { data, loading } = useQuery(GET_DATASET_VERSION_FILE_SAMPLE, {
    variables: {
      id: props.file.id,
    },
  });

  const { sample, columns, status } = useMemo(() => {
    if (data?.datasetVersionFile?.fileSample?.status === "FINISHED") {
      const sample = data.datasetVersionFile.fileSample.sample;
      return {
        sample,
        columns: sample.length > 0 ? Object.keys(sample[0]) : [],
        status: "FINISHED",
      };
    } else if (
      !data?.datasetVersionFile?.fileSample ||
      data?.datasetVersionFile?.fileSample?.status === "PROCESSING"
    ) {
      return {
        sample: [],
        columns: [],
        status: "PROCESSING",
      };
    }
    return {
      sample: [],
      columns: [],
      status: "ERROR",
    };
  }, [data]);

  if (loading)
    return (
      <div className="flex justify-center items-center h-24 p-4">
        <Spinner size="md" />
      </div>
    );

  if (status === "ERROR") {
    return (
      <div className="text-sm text-gray-500 italic w-full flex justify-center p-4">
        {t("We were not able to generate a sample for this file.")}
      </div>
    );
  } else if (status === "PROCESSING") {
    return (
      <div className="text-sm text-gray-500 italic w-full flex justify-center p-4">
        {t("Generating sample...")}
      </div>
    );
  } else if (status === "FINISHED") {
    return (
      <div className="space-y-4 mt-4">
        <code>
          <DescriptionList>
            <DescriptionList.Item label={t("Columns")}>
              {columns.length}
            </DescriptionList.Item>
            <DescriptionList.Item label={t("Rows in sample")}>
              {sample.length}
            </DescriptionList.Item>
          </DescriptionList>
        </code>

        <DataGrid
          data={sample}
          sortable
          spacing="tight"
          className="border border-gray-100 rounded-md overflow-hidden font-mono tracking-tight"
        >
          {columns.map((col) => (
            <TextColumn id={col} label={col} accessor={col} key={col} />
          ))}
        </DataGrid>
      </div>
    );
  } else {
    return null;
  }
};

DatasetVersionFileSample.fragments = {
  file: gql`
    fragment DatasetVersionFileSample_file on DatasetVersionFile {
      id
      contentType
    }
  `,
};

export default DatasetVersionFileSample;
