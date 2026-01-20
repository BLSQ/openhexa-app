import { gql } from "@apollo/client";
import clsx from "clsx";
import DescriptionList from "core/components/DescriptionList";
import Filesize from "core/components/Filesize";
import Overflow from "core/components/Overflow";
import Tabs from "core/components/Tabs";
import Time from "core/components/Time";
import Title from "core/components/Title";
import { useTranslation } from "next-i18next";
import DatasetVersionFileSample from "../DatasetVersionFileSample";
import DownloadVersionFile from "../DownloadVersionFile";
import { DatasetExplorer_VersionFragment } from "./DatasetExplorer.generated";
import ErrorBoundary from "core/components/ErrorBoundary";
import DatasetVersionFileColumns from "../DatasetVersionFileColumns";
import Pagination from "core/components/Pagination";
import { DatasetExplorer_FileFragment } from "./fragments.generated";
import Tooltip from "core/components/Tooltip";

type DatasetExplorerProps = {
  version: DatasetExplorer_VersionFragment;
  currentFile: NonNullable<DatasetExplorer_FileFragment>;
  onClickFile: (file: DatasetExplorer_FileFragment) => void;
  perPage: number;
  onPageChange: (page: number) => void;
};

const DatasetExplorer = ({
  version,
  currentFile,
  onClickFile,
  perPage,
  onPageChange,
}: DatasetExplorerProps) => {
  const { t } = useTranslation();
  const { files } = version;

  return (
    <div className="flex divide-x divide-b-50 h-full">
      <div className="min-w-42 xl:min-w-60 xl:max-w-max shrink flex flex-col my-1">
        <Overflow vertical className="flex-1 overflow-hidden">
          <ul>
            {version.files.items.map((file) => (
              <li
                key={file.id}
                onClick={() => onClickFile(file)}
                className={clsx(
                  "pl-6 pr-3 py-2 text-xs font-mono tracking-tighter hover:bg-gray-100 hover:text-gray-900 cursor-pointer",
                  currentFile.id === file.id &&
                    "bg-gray-100 text-gray-800 font-semibold",
                )}
              >
                <Tooltip
                  label={file.filename}
                  placement="right"
                  renderTrigger={(ref) => (
                    <span
                      ref={ref}
                      className="block truncate whitespace-nowrap max-w-[30ch] xl:max-w-[50ch]"
                    >
                      {file.filename}
                    </span>
                  )}
                />
              </li>
            ))}
          </ul>
        </Overflow>
        <Pagination
          className="border-t px-2 py-2"
          page={files.pageNumber}
          perPage={perPage}
          countItems={files.items.length}
          totalItems={files.totalItems}
          onChange={onPageChange}
        />
      </div>
      <div className="flex-1 py-2 space-y-4 min-w-0">
        <div className="px-4 py-1 space-y-6">
          <Title level={3} className="flex justify-between gap-4 min-w-0">
            <div className="min-w-0 flex-1">
              <Tooltip
                label={currentFile.filename}
                placement="top"
                renderTrigger={(ref) => (
                  <span
                    ref={ref}
                    className="font-mono tracking-tight truncate whitespace-nowrap block"
                  >
                    {currentFile.filename}
                  </span>
                )}
              />
            </div>
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
  version: gql`
    fragment DatasetExplorer_version on DatasetVersion {
      id
      files(page: $page, perPage: $perPage) {
        totalPages
        pageNumber
        totalItems
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
