import { gql } from "@apollo/client";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import useCacheKey from "core/hooks/useCacheKey";
import { useState } from "react";
import { useTranslation } from "next-i18next";
import { deleteDatasetVersion } from "datasets/helpers/dataset";
import { DeleteDatasetVersionDialog_VersionFragment } from "./DeleteDatasetVersionDialog.generated";
import { ExclamationTriangleIcon } from "@heroicons/react/24/outline";

type DeleteDatasetVersionDialogProps = {
  open: boolean;
  onClose: () => void;
  onDelete?: () => void;
  version: DeleteDatasetVersionDialog_VersionFragment;
};

const DeleteDatasetVersionDialog = ({
  open,
  onClose,
  onDelete,
  version,
}: DeleteDatasetVersionDialogProps) => {
  const { t } = useTranslation();
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState("");
  const clearCache = useCacheKey("datasets");

  const handleDelete = async () => {
    setIsDeleting(true);
    setError("");

    try {
      await deleteDatasetVersion(version.id);
      clearCache();
      onDelete?.();
      onClose();
    } catch (err: any) {
      setError(err.message || t("An error occurred while deleting the version"));
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={() => {
        onClose();
        setError("");
      }}
      maxWidth="max-w-lg"
    >
      <div className="p-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="bg-red-100 p-3 rounded-full">
            <ExclamationTriangleIcon className="w-8 h-8 text-red-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {t("Delete Version")}
            </h2>
            <p className="text-sm text-gray-500">
              {t("This action cannot be undone")}
            </p>
          </div>
        </div>

        <div className="mb-6">
          <p className="text-gray-700">
            {t(
              'Are you sure you want to delete version "{{name}}"? All files and metadata associated with this version will be permanently deleted.',
              {
                name: version.name,
              },
            )}
          </p>
        </div>

        {error && (
          <div className="mb-4 text-red-600 text-sm bg-red-50 border border-red-200 rounded p-3">
            {error}
          </div>
        )}

        <div className="flex justify-end gap-4">
          <Button
            variant="white"
            onClick={() => {
              onClose();
              setError("");
            }}
            disabled={isDeleting}
          >
            {t("Cancel")}
          </Button>
          <Button variant="danger" onClick={handleDelete} disabled={isDeleting}>
            {isDeleting ? <Spinner size="xs" /> : t("Delete Version")}
          </Button>
        </div>
      </div>
    </Dialog>
  );
};

DeleteDatasetVersionDialog.fragments = {
  version: gql`
    fragment DeleteDatasetVersionDialog_version on DatasetVersion {
      id
      name
      dataset {
        slug
      }
      permissions {
        delete
      }
    }
  `,
};

export default DeleteDatasetVersionDialog;
