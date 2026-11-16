import Callout from "core/components/Callout";
import ConfirmSharingDialog from "core/features/Sharing/ConfirmSharingDialog";
import SharingPicker from "core/features/Sharing/SharingPicker";
import { SharingOption } from "core/features/Sharing/sharingStyles";
import { useTranslation } from "next-i18next";
import { ReactNode, useEffect, useState } from "react";

export type ShareDialogProps<V extends string> = {
  open: boolean;
  onClose: () => void;
  options: SharingOption<V>[];
  value: V;
  isOptionDisabled?: (value: V) => boolean;
  hint?: ReactNode;
  // Closes the dialog once resolved; a rejection keeps it open, the caller
  // being the one reporting the error.
  onSave: (next: V) => Promise<void>;
  // Both receive the visibility the dialog was opened with, so their content
  // does not flip while the saved value reaches the cache.
  warning?: (next: V, from: V) => ReactNode;
  children?: (next: V, from: V) => ReactNode;
};

const ShareDialog = <V extends string>({
  open,
  onClose,
  options,
  value,
  isOptionDisabled,
  hint,
  onSave,
  warning,
  children,
}: ShareDialogProps<V>) => {
  const { t } = useTranslation();
  const [from, setFrom] = useState(value);
  const [selected, setSelected] = useState(value);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (open) {
      setFrom(value);
      setSelected(value);
    }
    // Only on opening: the value changing under an open dialog is our own save.
  }, [open]);

  const save = async () => {
    if (selected === from) {
      onClose();
      return;
    }
    setSaving(true);
    try {
      await onSave(selected);
      onClose();
    } catch {
      // Reported by the caller.
    } finally {
      setSaving(false);
    }
  };

  const warningContent = warning?.(selected, from);

  return (
    <ConfirmSharingDialog
      open={open}
      title={t("Share")}
      confirmLabel={t("Save")}
      saving={saving}
      onClose={onClose}
      onConfirm={save}
    >
      <SharingPicker
        options={options}
        value={selected}
        onChange={setSelected}
        isOptionDisabled={(option) =>
          saving || (isOptionDisabled?.(option) ?? false)
        }
        hint={hint}
      />
      {warningContent && <Callout variant="warning">{warningContent}</Callout>}
      {children?.(selected, from)}
    </ConfirmSharingDialog>
  );
};

export default ShareDialog;
