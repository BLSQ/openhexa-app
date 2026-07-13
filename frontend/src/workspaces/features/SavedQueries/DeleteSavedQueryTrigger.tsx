import useCacheKey from "core/hooks/useCacheKey";
import { useTranslation } from "next-i18next";
import { ReactElement } from "react";
import { toast } from "react-toastify";
import {
  SavedQueryListItem_SavedQueryFragment,
  useDeleteSavedQueryMutation,
} from "workspaces/features/SavedQueries/SavedQueries.generated";

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
// button, we own the confirm + mutation + cache invalidation. Renders nothing
// when the user lacks delete permission.
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

  const [deleteSavedQuery] = useDeleteSavedQueryMutation();
  const clearCache = useCacheKey("savedQueries");

  const onClick = async () => {
    if (!window.confirm(confirmMessage)) {
      return;
    }
    try {
      const { data } = await deleteSavedQuery({
        variables: { input: { id: savedQuery.id } },
      });
      if (!data?.deleteSavedQuery.success) {
        throw new Error(t("Failed to delete the saved query."));
      }
      onDelete?.();
      clearCache();
      toast.success(t("Saved query deleted"));
    } catch (err: any) {
      toast.error(err.message);
    }
  };

  if (!savedQuery.permissions.delete) {
    return null;
  }
  return children({ onClick });
};

export default DeleteSavedQueryTrigger;
