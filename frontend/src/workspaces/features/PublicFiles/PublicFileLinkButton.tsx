import { LinkIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import { useTranslation } from "next-i18next";
import { toast } from "react-toastify";

type PublicFileLinkButtonProps = {
  url: string;
};

// Offered to every member who can see the file, not only to those who may
// open the folder: passing the link on is what a public file is for.
const PublicFileLinkButton = ({ url }: PublicFileLinkButtonProps) => {
  const { t } = useTranslation();

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(url);
      toast.success(t("Public link copied"));
    } catch {
      toast.error(t("Could not copy the public link"));
    }
  };

  return (
    <Button
      onClick={copy}
      variant="secondary"
      size="sm"
      title={t("Copy the public link")}
    >
      <LinkIcon className="h-4 w-4" />
    </Button>
  );
};

export default PublicFileLinkButton;
