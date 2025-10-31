import { useState } from "react";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { Organization_OrganizationFragment } from "organizations/graphql/queries.generated";
import { useDeleteOrganizationMutation } from "organizations/graphql/mutations.generated";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Input from "core/components/forms/Input";
import Spinner from "core/components/Spinner";
import { DeleteOrganizationError } from "graphql/types";
import {
  TrashIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";

type DeleteOrganizationDialogProps = {
  organization: Organization_OrganizationFragment;
};

const DeleteOrganizationDialog = ({
  organization,
}: DeleteOrganizationDialogProps) => {
  const { t } = useTranslation();
  const router = useRouter();
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [confirmationText, setConfirmationText] = useState("");
  const [deleteError, setDeleteError] = useState("");

  const [deleteOrganization, { loading: deleteLoading }] =
    useDeleteOrganizationMutation();

  const confirmationPhrase = t("delete organization forever");

  const handleDelete = async () => {
    if (confirmationText.toLowerCase() !== confirmationPhrase.toLowerCase()) {
      setDeleteError(
        t('Please type "{{phrase}}" to confirm', {
          phrase: confirmationPhrase,
        }),
      );
      return;
    }

    try {
      const { data } = await deleteOrganization({
        variables: {
          input: {
            id: organization.id,
          },
        },
      });

      if (data?.deleteOrganization.success) {
        router.push("/organizations").then();
      } else {
        const errors = data?.deleteOrganization.errors ?? [];
        if (errors.includes(DeleteOrganizationError.PermissionDenied)) {
          setDeleteError(
            t("You don't have permission to delete this organization"),
          );
        } else {
          setDeleteError(
            t("An error occurred while deleting the organization"),
          );
        }
      }
    } catch (error) {
      setDeleteError(t("An error occurred while deleting the organization"));
    }
  };

  return (
    <>
      <div className="pt-6 border-t border-gray-200">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <TrashIcon className="w-5 h-5 text-red-600" />
            </div>
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-medium text-gray-900">
              {t("Delete Organization")}
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              {t(
                "Permanently delete this organization and all its data. This action cannot be undone.",
              )}
            </p>
            <Button
              variant="danger"
              onClick={() => setIsDeleteDialogOpen(true)}
              className="mt-3"
              size="sm"
            >
              {t("Delete Organization")}
            </Button>
          </div>
        </div>
      </div>

      <Dialog
        open={isDeleteDialogOpen}
        onClose={() => {
          setIsDeleteDialogOpen(false);
          setConfirmationText("");
          setDeleteError("");
        }}
        maxWidth="max-w-2xl"
      >
        <div className="p-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="bg-red-100 p-3 rounded-full">
              <ExclamationTriangleIcon className="w-8 h-8 text-red-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {t("Delete Organization")}
              </h2>
              <p className="text-sm text-gray-500">
                {t("This action cannot be undone")}
              </p>
            </div>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-yellow-900 mb-2">
              {t("Warning: This will permanently delete")}
            </h3>
            <ul className="list-disc list-inside space-y-1 text-yellow-800">
              <li>
                {t("Organization")}: <strong>{organization.name}</strong>
              </li>
              <li>
                {t("All {{count}} associated workspaces", {
                  count: organization.workspaces.totalItems,
                })}
              </li>
              <li>
                {t("All {{count}} members accesses", {
                  count: organization.members.totalItems,
                })}
              </li>
            </ul>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('Type "{{phrase}}" to confirm', {
                phrase: confirmationPhrase,
              })}
            </label>
            <Input
              type="text"
              value={confirmationText}
              onChange={(e) => {
                setConfirmationText(e.target.value);
                setDeleteError("");
              }}
              placeholder={confirmationPhrase}
              className="w-full"
            />
          </div>

          {deleteError && (
            <div className="mb-4 text-red-600 text-sm bg-red-50 border border-red-200 rounded p-3">
              {deleteError}
            </div>
          )}

          <div className="flex justify-end gap-4">
            <Button
              variant="white"
              onClick={() => {
                setIsDeleteDialogOpen(false);
                setConfirmationText("");
                setDeleteError("");
              }}
            >
              {t("Cancel")}
            </Button>
            <Button
              variant="danger"
              onClick={handleDelete}
              disabled={
                deleteLoading ||
                confirmationText.toLowerCase() !==
                  confirmationPhrase.toLowerCase()
              }
            >
              {deleteLoading ? <Spinner size="xs" /> : t("Delete Organization")}
            </Button>
          </div>
        </div>
      </Dialog>
    </>
  );
};

export default DeleteOrganizationDialog;
