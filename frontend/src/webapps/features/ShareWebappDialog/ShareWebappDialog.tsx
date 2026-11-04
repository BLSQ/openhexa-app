import {
  ExclamationTriangleIcon,
  GlobeAltIcon,
  UsersIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import Button from "core/components/Button";
import Clipboard from "core/components/Clipboard";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import { WebappType } from "graphql/types";
import { useTranslation } from "next-i18next";
import { ReactNode, useEffect, useState } from "react";

type ShareWebappDialogProps = {
  open: boolean;
  onClose: () => void;
  onSave: (isPublic: boolean) => Promise<void>;
  webapp: {
    isPublic: boolean;
    serveUrl: string;
    type: WebappType;
  };
};

type AudienceOptionProps = {
  checked: boolean;
  onSelect: () => void;
  icon: ReactNode;
  label: string;
  description: string;
};

const AudienceOption = ({
  checked,
  onSelect,
  icon,
  label,
  description,
}: AudienceOptionProps) => (
  <label
    className={clsx(
      "flex cursor-pointer items-start gap-3 rounded-md border p-3",
      checked
        ? "border-blue-500 bg-blue-50"
        : "border-gray-200 hover:bg-gray-50",
    )}
  >
    <input
      type="radio"
      name="audience"
      checked={checked}
      onChange={onSelect}
      className="mt-1 h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-500"
    />
    <span className="flex items-start gap-2">
      <span className="mt-0.5 text-gray-500">{icon}</span>
      <span>
        <span className="block text-sm font-medium text-gray-900">{label}</span>
        <span className="block text-sm text-gray-500">{description}</span>
      </span>
    </span>
  </label>
);

const ShareWebappDialog = ({
  open,
  onClose,
  onSave,
  webapp,
}: ShareWebappDialogProps) => {
  const { t } = useTranslation();
  const [isPublic, setIsPublic] = useState(webapp.isPublic);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Reopening starts from the saved choice, not from a previous selection.
  useEffect(() => {
    if (open) {
      setIsPublic(webapp.isPublic);
    }
  }, [open, webapp.isPublic]);

  const isDirty = isPublic !== webapp.isPublic;
  const isStatic = webapp.type === WebappType.Static;

  const handleSave = async () => {
    if (!isDirty || isSubmitting) return;
    setIsSubmitting(true);
    try {
      await onSave(isPublic);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="max-w-xl">
      <Dialog.Title onClose={onClose}>{t("Share web app")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <div className="rounded-md bg-gray-50 p-3">
          <p className="mb-1 text-xs font-medium text-gray-500">
            {t("Web app link")}
          </p>
          <Clipboard value={webapp.serveUrl}>
            <code className="text-sm text-gray-800">{webapp.serveUrl}</code>
          </Clipboard>
        </div>

        <div className="space-y-2">
          <p className="text-xs font-medium text-gray-500">
            {t("Who can open the link")}
          </p>
          <AudienceOption
            checked={!isPublic}
            onSelect={() => setIsPublic(false)}
            icon={<UsersIcon className="h-5 w-5" />}
            label={t("Workspace members")}
            description={t(
              "Members of this workspace sign in to open it. The web app stays private.",
            )}
          />
          <AudienceOption
            checked={isPublic}
            onSelect={() => setIsPublic(true)}
            icon={<GlobeAltIcon className="h-5 w-5" />}
            label={t("Anyone with the link")}
            description={t(
              "No OpenHEXA account is needed. The web app becomes public.",
            )}
          />
        </div>

        {isStatic && isPublic && (
          <div className="flex gap-3 rounded-md border border-amber-200 bg-amber-50 p-3">
            <ExclamationTriangleIcon className="h-5 w-5 flex-none text-amber-600" />
            <div>
              <p className="text-sm text-amber-900">
                {t(
                  "Visitors are not signed in. The web app's API calls reach every public dataset, pipeline, file and saved query of this workspace, and nothing else.",
                )}
              </p>
              <p className="mt-1 text-xs text-amber-800">
                {t(
                  "Make a resource public from its own page for the app to reach it.",
                )}
              </p>
            </div>
          </div>
        )}
        {isStatic && !isPublic && (
          <p className="text-sm text-gray-500">
            {t(
              "API requests run on behalf of the signed-in member, limited to the operations enabled under Workspace permissions.",
            )}
          </p>
        )}
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose} disabled={isSubmitting}>
          {t("Cancel")}
        </Button>
        <Button
          onClick={handleSave}
          disabled={!isDirty || isSubmitting}
          data-testid="share-save"
        >
          {isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Save")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default ShareWebappDialog;
