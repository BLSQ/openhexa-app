import { LinkIcon } from "@heroicons/react/24/outline";
import { useTranslation } from "next-i18next";
import { toast } from "react-toastify";
import { GHOST } from "workspaces/features/DataStudioEditor/toolbarStyles";
import { getPublicSavedQueryUrl } from "workspaces/features/SavedQueries/savedQueryVisibility";

type PublicSavedQueryLinkButtonProps = {
  slug: string;
};

// Toolbar control of a public query: copies its permalink. Offered to every
// member who can see the query, not only to those who may change its
// visibility, since passing the link on is what a public query is for.
const PublicSavedQueryLinkButton = ({
  slug,
}: PublicSavedQueryLinkButtonProps) => {
  const { t } = useTranslation();

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(getPublicSavedQueryUrl(slug));
      toast.success(t("Public link copied"));
    } catch {
      toast.error(t("Could not copy the public link"));
    }
  };

  return (
    <button
      type="button"
      onClick={copy}
      title={t("Copy the public link")}
      className={GHOST}
    >
      <LinkIcon className="h-4 w-4" />
      {t("Public link")}
    </button>
  );
};

export default PublicSavedQueryLinkButton;
