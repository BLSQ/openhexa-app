import { gql } from "@apollo/client";
import clsx from "clsx";
import DescriptionList from "core/components/DescriptionList";
import Overflow from "core/components/Overflow";
import Tabs from "core/components/Tabs";
import Time from "core/components/Time";
import Title from "core/components/Title";
import { useTranslation } from "react-i18next";
import DownloadVersionFile from "../DownloadVersionFile";
import {
  DatasetExplorer_FileFragment,
  DatasetExplorer_VersionFragment,
} from "./DatasetExplorer.generated";
import DatasetVersionFileSample from "../DatasetVersionFileSample";
import { DocumentIcon } from "@heroicons/react/24/outline";
import Filesize from "core/components/Filesize";

type DatasetExplorerProps = {
  version: DatasetExplorer_VersionFragment;
  currentFile?: DatasetExplorer_FileFragment | null;
  onClickFile: (file: DatasetExplorer_FileFragment) => void;
};

const DatasetExplorer = ({
  version,
  currentFile,
  onClickFile,
}: DatasetExplorerProps) => {
  const { t } = useTranslation();

  return (
    <div className="flex divide-x divide-b-50 min-h-[70vh]">
      <Overflow
        vertical
        className="basis-1/3 max-w-max shrink overflow-hidden my-1"
      >
        <ul>
          {version.files.items.map((file) => (
            <li
              key={file.id}
              onClick={() => onClickFile(file)}
              title={file.filename}
              className={clsx(
                "pl-6 pr-3 py-2 text-xs font-mono tracking-tighter hover:bg-gray-100 hover:text-gray-900 cursor-pointer truncate text-ellipsis max-w-[50ch]",
                currentFile?.id === file.id &&
                  "bg-gray-100 text-gray-800 font-semibold",
              )}
            >
              {file.filename}
            </li>
          ))}
        </ul>
      </Overflow>
      <div className="flex-1 py-2 space-y-4">
        {currentFile && (
          <div className="px-4 py-1 space-y-6">
            <Title level={3} className="flex justify-between">
              <span className="font-mono tracking-tighter">
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
              <Tabs.Tab label={t("Sample")} className="space-y-2 mt-2">
                <DatasetVersionFileSample file={currentFile} />
              </Tabs.Tab>
            </Tabs>
          </div>
        )}
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
      contentType
      size
      uri
    }
    ${DownloadVersionFile.fragments.file}
    ${DatasetVersionFileSample.fragments.file}
  `,
  version: gql`
    fragment DatasetExplorer_version on DatasetVersion {
      id
      files {
        items {
          ...DatasetExplorer_file
        }
      }
    }
  `,
};

export default DatasetExplorer;
