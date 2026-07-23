import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import { useTranslation } from "next-i18next";
import { ReactElement, useState } from "react";
import { toast } from "react-toastify";
import { SavedQueryListItem_SavedQueryFragment } from "workspaces/features/SavedQueries/SavedQueries.generated";
import { useSavedQueryMutations } from "workspaces/features/SavedQueries/useSavedQueryMutations";

type DeleteSavedQueryTriggerProps = {
  savedQuery: Pick<
    SavedQueryListItem_SavedQueryFragment,
    "id" | "name" | "permissions"
  >;
  children: ({ onClick }: { onClick: () => void }) => ReactElement;
  onDelete?: () => void;
  confirmMessage?: string;
};

// Render-prop trigger (mirrors DeleteDatasetTrigger): the caller supplies the
// button, we own the confirm dialog + mutation + cache invalidation. Renders
// nothing when the user lacks delete permission.
const DeleteSavedQueryTrigger = (props: DeleteSavedQueryTriggerProps) => {
  const { t } = useTranslation();
  const {
    savedQuery,
    onDelete,
    children,
    confirmMessage = t(
      'Are you sure you want to delete the query "{{name}}"? This cannot be undone.',
      { name: savedQuery.name },
    ),
  } = props;

  const [open, setOpen] = useState(false);
  const { remove, removing } = useSavedQueryMutations();

  const onConfirm = async () => {
    try {
      const res = await remove(savedQuery.id);
      if (res.ok) {
        onDelete?.();
        toast.success(t("Saved query deleted"));
        setOpen(false);
      } else {
        toast.error(res.message);
      }
    } catch (err: any) {
      toast.error(err.message);
    }
  };

  if (!savedQuery.permissions.delete) {
    return null;
  }

  return (
    <>
      {children({ onClick: () => setOpen(true) })}
      <Dialog
        open={open}
        onClose={() => !removing && setOpen(false)}
        maxWidth="max-w-md"
      >
        <Dialog.Title onClose={() => setOpen(false)}>
          {t("Delete saved query")}
        </Dialog.Title>
        <Dialog.Content>
          <p className="text-sm text-gray-600">{confirmMessage}</p>
        </Dialog.Content>
        <Dialog.Actions>
          <Button
            variant="outlined"
            onClick={() => setOpen(false)}
            disabled={removing}
          >
            {t("Cancel")}
          </Button>
          <Button variant="danger" onClick={onConfirm} disabled={removing}>
            {t("Delete")}
          </Button>
        </Dialog.Actions>
      </Dialog>
    </>
  );
};

export default DeleteSavedQueryTrigger;
