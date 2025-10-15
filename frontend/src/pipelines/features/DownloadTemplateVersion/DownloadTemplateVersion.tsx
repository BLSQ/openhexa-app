import { gql } from "@apollo/client";
import { downloadTemplateVersion } from "workspaces/helpers/templates";
import { useState } from "react";
import { DownloadTemplateVersion_VersionFragment } from "./DownloadTemplateVersion.generated";

type DownloadTemplateVersionProps = {
  version: DownloadTemplateVersion_VersionFragment;
  children({
    onClick,
    isDownloading,
  }: {
    onClick(): void;
    isDownloading: boolean;
  }): React.ReactElement;
};
const DownloadTemplateVersion = (props: DownloadTemplateVersionProps) => {
  const { version, children } = props;
  const [isDownloading, setDownloading] = useState(false);
  const onClick = () => {
    setDownloading(true);
    downloadTemplateVersion(
      version.id,
      version.template.code,
      version.versionNumber,
      version.sourcePipelineVersion.id,
    );
    setDownloading(false);
  };

  return children({ onClick, isDownloading });
};

DownloadTemplateVersion.fragments = {
  version: gql`
    fragment DownloadTemplateVersion_version on PipelineTemplateVersion {
      id
      versionNumber
      template {
        code
      }
      sourcePipelineVersion {
        id
      }
    }
  `,
};

export default DownloadTemplateVersion;
