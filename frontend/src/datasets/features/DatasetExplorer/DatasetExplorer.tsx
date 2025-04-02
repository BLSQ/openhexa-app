import { gql } from "@apollo/client";
import clsx from "clsx";
import DescriptionList from "core/components/DescriptionList";
import Filesize from "core/components/Filesize";
import Overflow from "core/components/Overflow";
import Tabs from "core/components/Tabs";
import Time from "core/components/Time";
import Title from "core/components/Title";
import { useTranslation } from "react-i18next";
import DatasetVersionFileSample from "../DatasetVersionFileSample";
import DownloadVersionFile from "../DownloadVersionFile";
import {
  DatasetExplorer_FileFragment,
  DatasetExplorer_VersionFragment,
} from "./DatasetExplorer.generated";
import ErrorBoundary from "core/components/ErrorBoundary";
import DatasetVersionFileColumns from "../DatasetVersionFileColumns";

type DatasetExplorerProps = {
  version: DatasetExplorer_VersionFragment;
  currentFile: NonNullable<DatasetExplorer_FileFragment>;
  onClickFile: (file: DatasetExplorer_FileFragment) => void;
};

const DatasetExplorer = ({
  version,
  currentFile,
  onClickFile,
}: DatasetExplorerProps) => {
  const { t } = useTranslation();

  return (
    <div className="flex divide-x divide-b-50 ">
      <Overflow
        vertical
        className="min-w-42 xl:min-w-60 xl:max-w-max shrink overflow-hidden my-1"
      >
        <ul>
          {version.files.items.map((file) => (
            <li
              key={file.id}
              onClick={() => onClickFile(file)}
              title={file.filename}
              className={clsx(
                "pl-6 pr-3 py-2 text-xs font-mono tracking-tighter hover:bg-gray-100 hover:text-gray-900 cursor-pointer truncate text-ellipsis max-w-[30ch] xl:max-w-[50ch]",
                currentFile.id === file.id &&
                  "bg-gray-100 text-gray-800 font-semibold",
              )}
            >
              {file.filename}
            </li>
          ))}
        </ul>
      </Overflow>
      <div className="flex-1 py-2 space-y-4 min-w-0">
        <div className="px-4 py-1 space-y-6">
          <Title level={3} className="flex justify-between gap-4">
            <span className="font-mono tracking-tight">
              {currentFile.filename}
            </span>
            <DownloadVersionFile
              file={currentFile}
              variant="secondary"
              size="sm"
            />
          </Title>
          <DescriptionList compact>
            <DescriptionList.Item label={t("Created at")}>
              <Time datetime={currentFile.createdAt} />
            </DescriptionList.Item>
            <DescriptionList.Item label={t("Created by")}>
              {currentFile.createdBy?.displayName ?? "-"}
            </DescriptionList.Item>
            <DescriptionList.Item label={t("Type")}>
              <code className="font-mono text-sm text-gray-600">
                {currentFile.contentType}
              </code>
            </DescriptionList.Item>
            <DescriptionList.Item label={t("Size")}>
              <code className="font-mono text-sm text-gray-600">
                <Filesize size={currentFile.size} />
              </code>
            </DescriptionList.Item>
          </DescriptionList>
          <Tabs>
            <Tabs.Tab
              label={t("Preview")}
              className="mt-2 min-h-[560px] xtall:min-h-[780px] relative"
            >
              <ErrorBoundary fullScreen={false}>
                <DatasetVersionFileSample
                  file={currentFile}
                  version={version}
                />
              </ErrorBoundary>
            </Tabs.Tab>
            <Tabs.Tab
              label={t("Columns")}
              className="mt-2 min-h-[560px] xtall:min-h-[780px] relative"
            >
              <DatasetVersionFileColumns file={currentFile} version={version} />
            </Tabs.Tab>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

DatasetExplorer.fragments = {
  file: gql`
    fragment DatasetExplorer_file on DatasetVersionFile {
      id
      filename
      createdAt
      createdBy {
        displayName
      }
      ...DownloadVersionFile_file
      ...DatasetVersionFileSample_file
      ...DatasetVersionFileColumns_file
      contentType
      size
      uri
    }
    ${DownloadVersionFile.fragments.file}
    ${DatasetVersionFileSample.fragments.file}
    ${DatasetVersionFileColumns.fragments.file}
  `,
  version: gql`
    fragment DatasetExplorer_version on DatasetVersion {
      id
      files {
        items {
          ...DatasetExplorer_file
        }
      }
      ...DatasetVersionFileSample_version
      ...DatasetVersionFileColumns_version
    }
    ${DatasetVersionFileSample.fragments.version}
    ${DatasetVersionFileColumns.fragments.version}
  `,
};

export default DatasetExplorer;
