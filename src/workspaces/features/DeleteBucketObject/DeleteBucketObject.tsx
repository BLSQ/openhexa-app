import { gql } from "@apollo/client";
import { TrashIcon } from "@heroicons/react/24/outline";
import { ReactElement } from "react";
import { useTranslation } from "next-i18next";
import { deleteBucketObject } from "workspaces/helpers/bucket";

import Button from "core/components/Button";
import {
  DeleteBucketObject_ObjectFragment,
  DeleteBucketObject_WorkspaceFragment,
} from "./DeleteBucketObject.generated";
import { BucketObjectType } from "graphql/types";
import { toast } from "react-toastify";

type DeleteBucketObjectProps = {
  children?({ onClick }: { onClick(): void }): ReactElement;
  workspace: DeleteBucketObject_WorkspaceFragment;
  object: DeleteBucketObject_ObjectFragment;
};

const DeleteBucketObject = (props: DeleteBucketObjectProps) => {
  const { children, workspace, object } = props;
  const { t } = useTranslation();

  if (!workspace.permissions.deleteObject) return null;

  const onClick = async () => {
    const deleteMessage =
      object.type === BucketObjectType.Directory
        ? t(
            "Are you sure to delete this directory ? It will delete all its content.",
          )
        : t("Are you sure to delete this file ?");
    if (window.confirm(deleteMessage))
      try {
        await deleteBucketObject(workspace.slug, object.key);
      } catch (err) {
        toast.error(t("Unexpected error"));
      }
  };

  if (children) {
    return children({ onClick });
  }

  return (
    <Button
      onClick={onClick}
      variant="danger"
      leadingIcon={<TrashIcon className="h-4 w-4" />}
    >
      {t("Delete")}
    </Button>
  );
};

DeleteBucketObject.fragments = {
  workspace: gql`
    fragment DeleteBucketObject_workspace on Workspace {
      slug
      permissions {
        deleteObject
      }
    }
  `,
  object: gql`
    fragment DeleteBucketObject_object on BucketObject {
      key
      name
      type
    }
  `,
};

export default DeleteBucketObject;
