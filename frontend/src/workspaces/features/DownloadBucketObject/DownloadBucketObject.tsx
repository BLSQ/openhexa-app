import { gql } from "@apollo/client";
import Button from "core/components/Button";
import type { ButtonProps } from "core/components/Button/Button";
import Spinner from "core/components/Spinner";
import { type ReactElement, useState } from "react";
import { useTranslation } from "next-i18next";
import {
  downloadURL,
  getBucketObjectDownloadUrl,
} from "workspaces/helpers/bucket";
import type {
  DownloadBucketObject_ObjectFragment,
  DownloadBucketObject_WorkspaceFragment,
} from "./DownloadBucketObject.generated";

type DownloadBucketObjectProps = {
  workspace: DownloadBucketObject_WorkspaceFragment;
  children?({
    isPreparing,
    onClick,
  }: {
    isPreparing: boolean;
    onClick(): void;
  }): ReactElement | null;
  object: DownloadBucketObject_ObjectFragment;
} & Omit<ButtonProps, "children">;

const DownloadBucketObject = (props: DownloadBucketObjectProps) => {
  const { workspace, object, children, ...delegated } = props;
  const [isPreparing, setIsPreparing] = useState(false);
  const { t } = useTranslation();

  const onClick = async () => {
    setIsPreparing(true);
    try {
      const url = await getBucketObjectDownloadUrl(workspace.slug, object.key);
      await downloadURL(url, "_blank");
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

DownloadBucketObject.fragments = {
  workspace: gql`
    fragment DownloadBucketObject_workspace on Workspace {
      slug
    }
  `,
  object: gql`
    fragment DownloadBucketObject_object on BucketObject {
      key
    }
  `,
};

export default DownloadBucketObject;
