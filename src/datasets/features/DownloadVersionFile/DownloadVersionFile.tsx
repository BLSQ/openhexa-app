import { gql } from "@apollo/client";
import { ArrowDownTrayIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import { ButtonProps } from "core/components/Button/Button";
import Spinner from "core/components/Spinner";
import { prepareVersionFileDownload } from "datasets/helpers/dataset";
import { useTranslation } from "next-i18next";
import { ReactElement, useState } from "react";
import { downloadURL } from "workspaces/helpers/bucket";
import { DownloadVersionFile_FileFragment } from "./DownloadVersionFile.generated";
import { toast } from "react-toastify";

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

  const onClick = async () => {
    setIsPreparing(true);
    try {
      const downloadUrl = await prepareVersionFileDownload(file.id);
      await downloadURL(downloadUrl);
    } catch (exc) {
      toast.error(
        t("We were not able to generate a download url for this file"),
      );
    } finally {
      setIsPreparing(false);
    }
  };

  if (children) {
    return children({ onClick, isPreparing }) || null;
  }

  return (
    <Button disabled={isPreparing} onClick={onClick} {...delegated}>
      {isPreparing ? (
        <Spinner size="xs" />
      ) : (
        <ArrowDownTrayIcon className="h-3 w-3" />
      )}
      <span className="ml-1.5">{t("Download")}</span>
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
