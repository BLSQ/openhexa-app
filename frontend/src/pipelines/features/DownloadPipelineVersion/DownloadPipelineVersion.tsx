import { gql } from "@apollo/client";
import { downloadPipelineVersion } from "pipelines/helpers/pipeline";
import { useState } from "react";
import { DownloadPipelineVersion_VersionFragment } from "./DownloadPipelineVersion.generated";

type DownloadPipelineVersionProps = {
  version: DownloadPipelineVersion_VersionFragment;
  children({
    onClick,
    isDownloading,
  }: {
    onClick(): void;
    isDownloading: boolean;
  }): React.ReactElement;
};
const DownloadPipelineVersion = (props: DownloadPipelineVersionProps) => {
  const { version, children } = props;
  const [isDownloading, setDownloading] = useState(false);
  const onClick = async () => {
    setDownloading(true);
    try {
      await downloadPipelineVersion(version.id);
    } catch (error) {
      console.error("Failed to download pipeline:", error);
    } finally {
      setDownloading(false);
    }
  };

  return children({ onClick, isDownloading });
};

DownloadPipelineVersion.fragments = {
  version: gql`
    fragment DownloadPipelineVersion_version on PipelineVersion {
      id
      name
      pipeline {
        id
        code
      }
    }
  `,
};

export default DownloadPipelineVersion;
