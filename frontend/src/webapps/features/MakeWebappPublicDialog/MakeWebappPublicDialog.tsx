import { ExclamationTriangleIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Clipboard from "core/components/Clipboard";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import { WebappType } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useState } from "react";

type MakeWebappPublicDialogProps = {
  open: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
  webapp: {
    serveUrl: string;
    type: WebappType;
  };
};

const MakeWebappPublicDialog = ({
  open,
  onClose,
  onConfirm,
  webapp,
}: MakeWebappPublicDialogProps) => {
  const { t } = useTranslation();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleConfirm = async () => {
    setIsSubmitting(true);
    try {
      await onConfirm();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="max-w-xl">
      <Dialog.Title onClose={onClose}>
        {t("Make this web app public?")}
      </Dialog.Title>
      <Dialog.Content className="space-y-4">
        <div className="flex gap-3 rounded-md border border-amber-200 bg-amber-50 p-3">
          <ExclamationTriangleIcon className="h-5 w-5 flex-none text-amber-600" />
          <p className="text-sm text-amber-900">
            {t(
              "Anyone with the link will be able to open this web app without an OpenHEXA account. You can make it private again at any time.",
            )}
          </p>
        </div>

        <div className="rounded-md bg-gray-50 p-3">
          <p className="mb-1 text-xs font-medium text-gray-500">
            {t("Public link")}
          </p>
          <Clipboard value={webapp.serveUrl}>
            <code className="text-sm text-gray-800">{webapp.serveUrl}</code>
          </Clipboard>
        </div>

        {webapp.type === WebappType.Static && (
          <div>
            <p className="text-sm text-gray-700">
              {t(
                "Visitors are not signed in. The web app's API calls reach every public dataset, pipeline, file and saved query of this workspace, and nothing else.",
              )}
            </p>
            <p className="mt-1 text-xs text-gray-500">
              {t(
                "Make a resource public from its own page for the app to reach it.",
              )}
            </p>
          </div>
        )}
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose} disabled={isSubmitting}>
          {t("Cancel")}
        </Button>
        <Button onClick={handleConfirm} disabled={isSubmitting}>
          {isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Make public")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default MakeWebappPublicDialog;
