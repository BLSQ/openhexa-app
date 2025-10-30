import { BookmarkIcon as OutlineBookmarkIcon } from "@heroicons/react/24/outline";
import { BookmarkIcon as SolidBookmarkIcon } from "@heroicons/react/24/solid";
import { gql } from "@apollo/client";
import useCacheKey from "core/hooks/useCacheKey";
import { toast } from "react-toastify";
import {
  useAddToShortcutsMutation,
  useRemoveFromShortcutsMutation,
} from "webapps/graphql/mutations.generated";
import { useTranslation } from "next-i18next";
import { ShortcutWebappButton_WebappFragment } from "./ShortcutWebappButton.generated";

type ShortcutWebappButtonProps = {
  webapp: ShortcutWebappButton_WebappFragment;
};

const ShortcutWebappButton = ({
  webapp: { id: webappId, isShortcut },
}: ShortcutWebappButtonProps) => {
  const { t } = useTranslation();
  const [addToShortcuts] = useAddToShortcutsMutation();
  const [removeFromShortcuts] = useRemoveFromShortcutsMutation();

  const clearCache = useCacheKey(["webapps", "shortcuts"]);

  const handleShortcutClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    try {
      if (isShortcut) {
        await removeFromShortcuts({
          variables: { input: { webappId } },
          refetchQueries: ["WorkspaceWebappsPage", "Shortcuts"],
        });
        toast.success(t("Removed from shortcuts"));
      } else {
        await addToShortcuts({
          variables: { input: { webappId } },
          refetchQueries: ["WorkspaceWebappsPage", "Shortcuts"],
        });
        toast.success(t("Added to shortcuts"));
      }
      clearCache();
    } catch (error) {
      toast.error(t("Error updating shortcuts"));
    }
  };

  const iconClassName = "h-5 w-5 group-hover/shortcut:scale-125 text-blue-500";

  const icon = isShortcut ? (
    <SolidBookmarkIcon className={iconClassName} />
  ) : (
    <OutlineBookmarkIcon strokeWidth={2} className={iconClassName} />
  );

  return (
    <button
      className={
        "cursor-pointer w-8 h-8 group/shortcut hover:p-1 transition-all flex items-center justify-center rounded-full"
      }
      onClick={handleShortcutClick}
      data-testid={`shortcut-button-${webappId}`}
      aria-label={isShortcut ? t("Remove from shortcuts") : t("Add to shortcuts")}
    >
      {icon}
    </button>
  );
};

ShortcutWebappButton.fragments = {
  webapp: gql`
    fragment ShortcutWebappButton_webapp on Webapp {
      id
      isShortcut
    }
  `,
};

export default ShortcutWebappButton;
