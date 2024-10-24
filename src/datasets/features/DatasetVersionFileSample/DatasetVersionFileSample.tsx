import { gql, useQuery } from "@apollo/client";
import DataGrid from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import DescriptionList from "core/components/DescriptionList";
import Spinner from "core/components/Spinner";
import { ApolloComponent } from "core/helpers/types";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";
import useFeature from "identity/hooks/useFeature";
import { DatasetVersionFileSample_FileFragment } from "./DatasetVersionFileSample.generated";

interface DatasetVersionFileSampleProps {
  file: DatasetVersionFileSample_FileFragment;
}

const NoPreviewMessage = () => {
  const { t } = useTranslation();
  return (
    <div className="text-sm text-gray-500 italic w-full flex justify-center p-4">
      {t("We cannot preview this file type.")}
    </div>
  );
};

const SmartPreviewer = ({
  file,
}: {
  file: DatasetVersionFileSample_FileFragment;
}) => {
  if (!file.downloadUrl || file.size > 100000000) return <NoPreviewMessage />;
  if (file.contentType.startsWith("image")) {
    return (
      <img
        src={file.downloadUrl}
        className="object-scale-down h-full w-full"
        alt={file.filename}
      />
    );
  } else if (file.contentType.startsWith("video")) {
    return (
      <video
        src={file.downloadUrl}
        className="object-scale-down w-full h-full"
        controls
      >
        <NoPreviewMessage />
      </video>
    );
  } else if (file.contentType.startsWith("audio")) {
    return (
      <audio src={file.downloadUrl} className="w-full h-full" controls>
        <NoPreviewMessage />
      </audio>
    );
  } else if (file.contentType.startsWith("text/html")) {
    return (
      <iframe
        sandbox="allow-scripts allow-forms allow-popups allow-presentation allow-modals allow-popups-to-escape-sandbox"
        src={file.downloadUrl}
        className="w-full h-full"
      ></iframe>
    );
  } else if (file.contentType.startsWith("text")) {
    return <iframe src={file.downloadUrl} className="w-full h-full"></iframe>;
  } else if (file.contentType.startsWith("application/pdf")) {
    return (
      <embed
        src={file.downloadUrl}
        type={file.contentType}
        width="100%"
        height="100%"
      ></embed>
    );
  }
  return <NoPreviewMessage />;
};

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
> = ({ file }) => {
  const { t } = useTranslation();
  const [isSmartPreviewerEnabled] = useFeature("datasets.smart_previewer");
  const { data, loading } = useQuery(GET_DATASET_VERSION_FILE_SAMPLE, {
    variables: {
      id: file.id,
    },
  });

  const { sample, columns, status } = useMemo(() => {
    if (!data?.datasetVersionFile.fileSample) {
      return {
        sample: [],
        columns: [],
        status: "UNSUPPORTED",
      };
    } else if (data.datasetVersionFile.fileSample.status === "FINISHED") {
      const sample = data.datasetVersionFile.fileSample.sample;
      return {
        sample,
        columns: sample.length > 0 ? Object.keys(sample[0]) : [],
        status: "FINISHED",
      };
    } else if (data.datasetVersionFile.fileSample.status === "PROCESSING") {
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

  switch (status) {
    case "UNSUPPORTED":
      return isSmartPreviewerEnabled ? (
        <SmartPreviewer file={file} />
      ) : (
        <NoPreviewMessage />
      );

    case "ERROR":
      return (
        <div className="text-sm text-gray-500 italic w-full flex justify-center p-4">
          {t("We were not able to generate a sample for this file.")}
        </div>
      );
    case "PROCESSING":
      return (
        <div className="text-sm text-gray-500 italic w-full flex justify-center p-4">
          {t("Generating sample...")}
        </div>
      );
    case "FINISHED":
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
  }
};

DatasetVersionFileSample.fragments = {
  file: gql`
    fragment DatasetVersionFileSample_file on DatasetVersionFile {
      id
      filename
      contentType
      size
      downloadUrl(attachment: false)
    }
  `,
};

export default DatasetVersionFileSample;
