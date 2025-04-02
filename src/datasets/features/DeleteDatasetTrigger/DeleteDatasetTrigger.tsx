import { gql } from "@apollo/client";
import useCacheKey from "core/hooks/useCacheKey";
import { useRouter } from "next/router";
import { ReactElement } from "react";
import { useTranslation } from "next-i18next";
import { deleteDataset } from "datasets/helpers/dataset";
import { DeleteDatasetTrigger_DatasetFragment } from "datasets/features/DeleteDatasetTrigger/DeleteDatasetTrigger.generated";
import { toast } from "react-toastify";

type DeleteDatasetTriggerProps = {
  children: ({ onClick }: { onClick: () => void }) => ReactElement;
  confirmMessage?: string;
  onDelete(): void;
  dataset: DeleteDatasetTrigger_DatasetFragment;
};

const DeleteDatasetTrigger = (props: DeleteDatasetTriggerProps) => {
  const { t } = useTranslation();
  const {
    dataset,
    onDelete,
    children,
    confirmMessage = t(
      'Are you sure you want to delete the dataset "{{name}}"? It will make it unavailable for all workspaces.',
      {
        name: dataset.name,
      },
    ),
  } = props;

  const clearCache = useCacheKey("datasets");

  const onClick = async () => {
    if (!window.confirm(confirmMessage)) {
      return;
    }
    try {
      await deleteDataset(dataset.id);
      if (onDelete) {
        await onDelete();
      }
      clearCache();
    } catch (err: any) {
      toast.error(err.message);
    }
  };

  if (!dataset.permissions.delete) {
    return null;
  }
  return children({ onClick });
};

DeleteDatasetTrigger.fragments = {
  dataset: gql`
    fragment DeleteDatasetTrigger_dataset on Dataset {
      id
      name
      workspace {
        slug
      }
      permissions {
        delete
      }
    }
  `,
};

export default DeleteDatasetTrigger;
