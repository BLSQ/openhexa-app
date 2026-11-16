import Field from "core/components/forms/Field";
import { ShareDialogProps } from "core/features/Sharing/ShareDialog";
import {
  canChangeDatasetVisibility,
  useDatasetSharingOptions,
} from "datasets/features/DatasetSharing/datasetSharing";
import { updateDataset } from "datasets/helpers/dataset";
import { DatasetVisibility } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import { toast } from "react-toastify";
import { DatasetShareButton_DatasetFragment } from "./DatasetShareButton.generated";

// The dataset's share dialog, shared by the header button and the Access
// management tab so both save, warn and claim the public slug the same way.
const useDatasetShareDialog = (
  dataset: DatasetShareButton_DatasetFragment,
): Omit<ShareDialogProps<DatasetVisibility>, "open" | "onClose"> => {
  const { t } = useTranslation();
  const options = useDatasetSharingOptions();
  const [publicSlug, setPublicSlug] = useState(
    dataset.publicSlug ?? dataset.slug,
  );
  const { visibility, permissions } = dataset;

  const onSave = async (next: DatasetVisibility) => {
    try {
      await updateDataset(dataset.id, {
        visibility: next,
        // Only sent while the dataset has none yet: it is locked once claimed.
        publicSlug:
          next === DatasetVisibility.Public && !dataset.publicSlug
            ? publicSlug
            : undefined,
      });
    } catch (error: any) {
      toast.error(error.message);
      throw error;
    }
  };

  return {
    options,
    value: visibility,
    onSave,
    isOptionDisabled: (option) =>
      !canChangeDatasetVisibility(visibility, option, {
        canUpdate: permissions.update,
        canShare: permissions.share,
      }),
    hint:
      !permissions.share &&
      visibility !== DatasetVisibility.Public &&
      t(
        "Only the author, workspace admins and organization admins can make a dataset public.",
      ),
    warning: (next, from) =>
      next !== from &&
      (next === DatasetVisibility.Public
        ? t(
            "Anyone with the link will be able to see this dataset without an OpenHEXA account. You can take it back at any time.",
          )
        : from === DatasetVisibility.Public &&
          t("The public link will stop working.")),
    children: (next) =>
      next === DatasetVisibility.Public && (
        <Field
          name="publicSlug"
          label={t("Public link identifier")}
          value={publicSlug}
          onChange={(event) => setPublicSlug(event.target.value)}
          disabled={Boolean(dataset.publicSlug)}
          help={t(
            "Part of the dataset's public link. It cannot be changed once set.",
          )}
          required
          fullWidth
        />
      ),
  };
};

export default useDatasetShareDialog;
