import { gql, useMutation } from "@apollo/client";
import Button from "core/components/Button";
import { ButtonProps } from "core/components/Button/Button";
import Spinner from "core/components/Spinner";
import { AlertType, displayAlert } from "core/helpers/alert";
import { ReactElement, useState } from "react";
import { useTranslation } from "next-i18next";
import { downloadURL } from "workspaces/helpers/bucket";
import {
  DownloadVersionFileMutation,
  DownloadVersionFileMutationVariables,
  DownloadVersionFile_FileFragment,
} from "./DownloadVersionFile.generated";
import { PrepareVersionFileDownloadError } from "graphql-types";

type DownloadVersionFileProps = {
  children?({
    isPreparing,
    onClick,
  }: {
    isPreparing: boolean;
    onClick(): void;
  }): ReactElement | null;
  file: DownloadVersionFile_FileFragment;
} & Omit<ButtonProps, "children">;

const DownloadVersionFile = (props: DownloadVersionFileProps) => {
  const { file, children, ...delegated } = props;
  const [isPreparing, setIsPreparing] = useState(false);
  const { t } = useTranslation();
  const [prepareDownload] = useMutation<
    DownloadVersionFileMutation,
    DownloadVersionFileMutationVariables
  >(gql`
    mutation DownloadVersionFile($input: PrepareVersionFileDownloadInput!) {
      prepareVersionFileDownload(input: $input) {
        success
        downloadUrl
        errors
      }
    }
  `);

  const onClick = async () => {
    setIsPreparing(true);
    try {
      const { data } = await prepareDownload({
        variables: { input: { fileId: file.id } },
      });
      if (data?.prepareVersionFileDownload.downloadUrl) {
        await downloadURL(data.prepareVersionFileDownload.downloadUrl);
      } else if (
        data?.prepareVersionFileDownload.errors.includes(
          PrepareVersionFileDownloadError.FileNotFound,
        )
      ) {
        displayAlert(t("This file is not yet uploaded"), AlertType.warning);
      } else if (
        data?.prepareVersionFileDownload.errors.includes(
          PrepareVersionFileDownloadError.PermissionDenied,
        )
      ) {
        displayAlert(
          t("You don't have permission to download this file"),
          AlertType.error,
        );
      } else {
        displayAlert(
          t("We were not able to generate a download url for this file"),
          AlertType.error,
        );
      }
    } finally {
      setIsPreparing(false);
    }
  };

  if (children) {
    return children({ onClick, isPreparing }) || null;
  }

  return (
    <Button disabled={isPreparing} onClick={onClick} {...delegated}>
      {isPreparing && <Spinner size="xs" className="mr-1" />}
      {t("Download")}
    </Button>
  );
};

DownloadVersionFile.fragments = {
  file: gql`
    fragment DownloadVersionFile_file on DatasetVersionFile {
      id
      filename
    }
  `,
};

export default DownloadVersionFile;
