import { gql, useQuery } from "@apollo/client";
import CodeEditor from "core/components/CodeEditor";
import DataGrid from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import DescriptionList from "core/components/DescriptionList";
import Spinner from "core/components/Spinner";
import { ApolloComponent } from "core/helpers/types";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  DatasetVersionFileSample_FileFragment,
  DatasetVersionFileSample_VersionFragment,
} from "./DatasetVersionFileSample.generated";
import { Iframe } from "core/components/Iframe";
import { trackEvent } from "core/helpers/analytics";

interface DatasetVersionFileSampleProps {
  file: DatasetVersionFileSample_FileFragment;
  version: DatasetVersionFileSample_VersionFragment;
}

const NoPreviewMessage = () => {
  const { t } = useTranslation();
  return (
    <div className="text-sm text-gray-500 italic w-full flex justify-center p-4">
      {t("We cannot preview this file type.")}
    </div>
  );
};

const CODE_LANG_BY_EXTENSION: Record<string, string> = {
  json: "json",
  geojson: "json",
  yaml: "yaml",
  yml: "yaml",
  xml: "xml",
};

const MAX_SIZE = 20_000_000;
const MAX_TEXT_SIZE = 5_000_000;

function getCodeLang(filename: string): string | null {
  const ext = filename.split(".").pop()?.toLowerCase();
  return ext ? (CODE_LANG_BY_EXTENSION[ext] ?? null) : null;
}

function canSmartPreview(file: DatasetVersionFileSample_FileFragment): boolean {
  return getCodeLang(file.filename) !== null;
}

const CodePreviewer = ({
  url,
  lang,
}: {
  url: string;
  lang: string;
}) => {
  const [content, setContent] = useState<string | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error();
        return res.text();
      })
      .then(setContent)
      .catch(() => setError(true));
  }, [url]);

  if (error) return <NoPreviewMessage />;
  if (content === null)
    return (
      <div className="flex justify-center items-center h-24 p-4">
        <Spinner size="md" />
      </div>
    );

  return (
    <CodeEditor
      value={content}
      lang={lang}
      readonly
      editable={false}
      height="720px"
    />
  );
};

const SmartPreviewer = ({
  file,
}: {
  file: DatasetVersionFileSample_FileFragment;
}) => {
  if (!file.downloadUrl || file.size > MAX_SIZE) return <NoPreviewMessage />;

  const codeLang = getCodeLang(file.filename);

  if (codeLang && file.size <= MAX_TEXT_SIZE) {
    return <CodePreviewer url={file.downloadUrl} lang={codeLang} />;
  }

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
      <Iframe
        autoResize
        sandbox="allow-presentation allow-modals allow-scripts allow-popups-to-escape-sandbox"
        src={file.downloadUrl}
        width="100%"
      ></Iframe>
    );
  } else if (file.contentType.startsWith("text")) {
    return (
      <Iframe
        autoResize
        sandbox="allow-presentation allow-modals allow-popups-to-escape-sandbox"
        src={file.downloadUrl}
        width="100%"
      ></Iframe>
    );
  } else if (file.contentType.startsWith("application/pdf")) {
    return (
      <embed
        src={file.downloadUrl}
        type={file.contentType}
        width="100%"
        height="720"
      ></embed>
    );
  }
  return <NoPreviewMessage />;
};

const GET_DATASET_VERSION_FILE_SAMPLE = gql`
  query GetDatasetVersionFileSample($id: ID!) {
    datasetVersionFile(id: $id) {
      id
      rows
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
> = ({ file, version }) => {
  const { t } = useTranslation();
  const { data, loading } = useQuery(GET_DATASET_VERSION_FILE_SAMPLE, {
    variables: {
      id: file.id,
    },
    skip: canSmartPreview(file),
  });

  useEffect(() => {
    const { dataset } = version;
    if (dataset) {
      trackEvent("datasets.dataset_file_previewed", {
        dataset_id: dataset.slug,
        workspace: dataset?.workspace?.slug,
        dataset_version: version.name,
        filename: file.filename,
      });
    }
  }, []);

  const { sample, columns, rows, status } = useMemo(() => {
    if (!data?.datasetVersionFile.fileSample) {
      return {
        sample: [],
        columns: [],
        rows: null,
        status: "UNSUPPORTED",
      };
    } else if (data.datasetVersionFile.fileSample.status === "FINISHED") {
      const sample = data.datasetVersionFile.fileSample.sample;
      const rows = data.datasetVersionFile.rows;
      const properties = data.datasetVersionFile.properties ?? {};
      const columnOrder: string[] | undefined = properties.column_order;
      const colsMapping: Record<string, string> = properties.columns ?? {};

      let columns: string[];
      if (columnOrder && colsMapping) {
        columns = columnOrder.map((key: string) => colsMapping[key]);
      } else if (sample.length > 0) {
        columns = Object.keys(sample[0]);
      } else {
        columns = [];
      }

      return {
        sample,
        columns,
        rows,
        status: "FINISHED",
      };
    } else if (data.datasetVersionFile.fileSample.status === "PROCESSING") {
      return {
        sample: [],
        columns: [],
        rows: null,
        status: "PROCESSING",
      };
    }
    return {
      sample: [],
      columns: [],
      rows: null,
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
      return <SmartPreviewer file={file} />;
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
          <DescriptionList>
            <DescriptionList.Item label={t("Columns")}>
              <code className="font-mono text-sm text-gray-600">
                {columns.length}
              </code>
            </DescriptionList.Item>
            <DescriptionList.Item label={t("Rows in dataset")}>
              <code className="font-mono text-sm text-gray-600">
                {rows ?? "n/a"}
              </code>
            </DescriptionList.Item>
          </DescriptionList>

          <DataGrid
            data={sample}
            sortable
            spacing="tight"
            className="border border-gray-100 rounded-md overflow-hidden tracking-tight"
            headerClassName="font-mono"
            rowClassName="font-mono"
            totalItems={sample.length}
            fixedLayout={false}
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
  version: gql`
    fragment DatasetVersionFileSample_version on DatasetVersion {
      name
      dataset {
        slug
        workspace {
          slug
        }
      }
    }
  `,
};

export default DatasetVersionFileSample;
