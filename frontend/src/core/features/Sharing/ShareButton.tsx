import { ShareIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import ShareDialog, {
  ShareDialogProps,
} from "core/features/Sharing/ShareDialog";
import { useTranslation } from "next-i18next";
import { useState } from "react";

// Header action of a shareable resource. Sharing lives behind its own dialog
// rather than in the edit form: who can reach a resource should never ride
// along with a rename.
const ShareButton = <V extends string>({
  collapseLabel,
  ...props
}: Omit<ShareDialogProps<V>, "open" | "onClose"> & {
  collapseLabel?: boolean;
}) => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button
        variant="white"
        leadingIcon={<ShareIcon className="h-4 w-4" />}
        onClick={() => setOpen(true)}
        collapseLabel={collapseLabel}
      >
        {t("Share")}
      </Button>
      <ShareDialog {...props} open={open} onClose={() => setOpen(false)} />
    </>
  );
};

export default ShareButton;
