import Callout from "core/components/Callout";
import ConfirmSharingDialog from "core/features/Sharing/ConfirmSharingDialog";
import SharingPicker from "core/features/Sharing/SharingPicker";
import useDatasetShareDialog from "datasets/features/DatasetSharing/useDatasetShareDialog";
import { DatasetVisibility } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import { DatasetShareButton_DatasetFragment } from "./DatasetShareButton.generated";

type DatasetVisibilityPickerProps = {
  dataset: DatasetShareButton_DatasetFragment;
  disabled?: boolean;
};

// Inline editor of the Access management tab. Switching between private and
// organization applies straight away, as it is easily undone; going public or
// leaving public asks for confirmation, with its warning and public slug.
const DatasetVisibilityPicker = ({
  dataset,
  disabled = false,
}: DatasetVisibilityPickerProps) => {
  const { t } = useTranslation();
  const { onSave, warning, children, ...picker } =
    useDatasetShareDialog(dataset);
  const { visibility } = dataset;
  const [pending, setPending] = useState<DatasetVisibility | null>(null);
  const [saving, setSaving] = useState(false);

  const save = async (next: DatasetVisibility) => {
    setSaving(true);
    try {
      await onSave(next);
      setPending(null);
    } catch {
      // Reported by onSave.
    } finally {
      setSaving(false);
    }
  };

  const select = (next: DatasetVisibility) => {
    if ([next, visibility].includes(DatasetVisibility.Public)) {
      setPending(next);
    } else {
      save(next);
    }
  };

  const makingPublic = pending === DatasetVisibility.Public;
  const warningContent = pending && warning?.(pending, visibility);

  return (
    <>
      <SharingPicker
        options={picker.options}
        value={visibility}
        onChange={select}
        isOptionDisabled={(option) =>
          disabled || saving || Boolean(picker.isOptionDisabled?.(option))
        }
        hint={!disabled && picker.hint}
      />
      <ConfirmSharingDialog
        open={pending !== null}
        title={
          makingPublic
            ? t("Make this dataset public?")
            : t("Stop sharing this dataset publicly?")
        }
        confirmLabel={
          makingPublic ? t("Make dataset public") : t("Stop sharing publicly")
        }
        saving={saving}
        onClose={() => setPending(null)}
        onConfirm={() => pending && save(pending)}
      >
        {warningContent && (
          <Callout variant="warning">{warningContent}</Callout>
        )}
        {pending && children?.(pending, visibility)}
      </ConfirmSharingDialog>
    </>
  );
};

export default DatasetVisibilityPicker;
