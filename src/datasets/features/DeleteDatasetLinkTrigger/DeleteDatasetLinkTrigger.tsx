import { gql } from "@apollo/client";
import useCacheKey from "core/hooks/useCacheKey";
import { useRouter } from "next/router";
import { ReactElement } from "react";
import { useTranslation } from "next-i18next";
import { deleteDatasetLink } from "datasets/helpers/dataset";
import { toast } from "react-toastify";

type DeleteDatasetLinkTriggerProps = {
  children: ({ onClick }: { onClick: () => void }) => ReactElement;
  confirmMessage?: string;
  datasetLink: any;
};

const DeleteDatasetLinkTrigger = (props: DeleteDatasetLinkTriggerProps) => {
  const { t } = useTranslation();
  const {
    datasetLink,
    children,
    confirmMessage = t(
      'Are you sure you want to delete the access to "{{name}}" for this workspace?',
      {
        name: datasetLink.dataset.name,
      },
    ),
  } = props;

  const clearCache = useCacheKey("datasets");

  const onClick = async () => {
    if (!window.confirm(confirmMessage)) {
      return;
    }
    try {
      await deleteDatasetLink(datasetLink.id);
    } catch (err: any) {
      toast.error(err.message);
    }

    clearCache();
  };

  if (!datasetLink.permissions.delete) {
    return null;
  }
  return children({ onClick });
};

DeleteDatasetLinkTrigger.fragments = {
  datasetLink: gql`
    fragment DeleteDatasetLinkTrigger_datasetLink on DatasetLink {
      id
      dataset {
        name
        id
      }
      workspace {
        slug
      }
      permissions {
        delete
      }
    }
  `,
};

export default DeleteDatasetLinkTrigger;
