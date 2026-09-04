import {
  ExclamationTriangleIcon,
  ShieldCheckIcon,
} from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import { WebappOperationScope } from "graphql/types";
import { Trans, useTranslation } from "next-i18next";
import { getScopeDescriptions } from "webapps/helpers";

type MakeWebappPublicDialogProps = {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  webapp: {
    name: string;
    allowedOperations: WebappOperationScope[];
  };
};

const MakeWebappPublicDialog = ({
  open,
  onClose,
  onConfirm,
  webapp,
}: MakeWebappPublicDialogProps) => {
  const { t } = useTranslation();
  const scopeDescriptions = getScopeDescriptions(t);
  const operations = webapp.allowedOperations ?? [];

  return (
    <Dialog open={open} onClose={onClose} maxWidth="max-w-2xl">
      <Dialog.Title>{t("Make this web app public")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <div className="flex gap-3 rounded-md border border-amber-200 bg-amber-50 p-3">
          <ExclamationTriangleIcon className="h-5 w-5 flex-none text-amber-600" />
          <div className="space-y-1 text-sm text-amber-900">
            <p className="font-medium">
              <Trans>
                Anyone on the internet will be able to open <b>{webapp.name}</b>
                .
              </Trans>
            </p>
            <p>
              {t(
                "Visitors will not need an OpenHEXA account and will not be asked to sign in. Do not make a web app public if it displays data that should stay within your workspace.",
              )}
            </p>
          </div>
        </div>

        <div className="rounded-md border border-gray-200 p-3">
          <p className="mb-2 text-sm font-medium text-gray-900">
            {t("What this web app can do in your workspace")}
          </p>
          {operations.length > 0 ? (
            <>
              <ul className="list-inside list-disc space-y-1 text-sm text-gray-700">
                {operations.map((scope) => (
                  <li key={scope}>{scopeDescriptions[scope].label}</li>
                ))}
              </ul>
              <p className="mt-2 text-xs text-gray-500">
                {t(
                  "Review these under Settings → API access before continuing.",
                )}
              </p>
            </>
          ) : (
            <p className="text-sm text-gray-500">
              {t("This web app has no API access to your workspace.")}
            </p>
          )}
        </div>

        <div className="flex gap-3 rounded-md border border-blue-200 bg-blue-50 p-3">
          <ShieldCheckIcon className="h-5 w-5 flex-none text-blue-600" />
          <p className="text-sm text-blue-900">
            {t(
              "Before it goes live, an AI security review will check this web app for issues that could expose your workspace. It becomes public once the review passes.",
            )}
          </p>
        </div>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button onClick={onConfirm}>{t("Start review")}</Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default MakeWebappPublicDialog;
