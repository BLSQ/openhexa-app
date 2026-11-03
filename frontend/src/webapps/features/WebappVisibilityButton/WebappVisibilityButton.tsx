import { gql } from "@apollo/client";
import {
  ExclamationTriangleIcon,
  GlobeAltIcon,
  LockClosedIcon,
} from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Clipboard from "core/components/Clipboard";
import Dialog from "core/components/Dialog";
import useCacheKey from "core/hooks/useCacheKey";
import { UpdateWebappError, WebappType } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import { toast } from "react-toastify";
import { useUpdateWebappMutation } from "webapps/graphql/mutations.generated";
import { WebappVisibilityButton_WebappFragment } from "./WebappVisibilityButton.generated";

type WebappVisibilityButtonProps = {
  webapp: WebappVisibilityButton_WebappFragment;
};

// Visibility lives behind a confirmation rather than in the edit form: making an
// app public puts it on the open internet, which should never ride along with a
// rename.
const WebappVisibilityButton = ({ webapp }: WebappVisibilityButtonProps) => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [updateWebapp] = useUpdateWebappMutation();
  const clearCache = useCacheKey("webapps");

  if (!webapp.permissions.update) {
    return null;
  }

  const makePublic = !webapp.isPublic;
  // Only static apps call the OpenHEXA API (through the proxy that public apps
  // are denied), so the API consequences only apply to them.
  const isStatic = webapp.type === WebappType.Static;
  const publicLink = webapp.serveUrl ?? webapp.url;

  const close = () => !saving && setIsOpen(false);

  const confirm = async () => {
    setSaving(true);
    try {
      const { data } = await updateWebapp({
        variables: { input: { id: webapp.id, isPublic: makePublic } },
      });
      if (data?.updateWebapp?.errors?.length) {
        toast.error(
          data.updateWebapp.errors[0] === UpdateWebappError.PermissionDenied
            ? t("You do not have permission to update this web app")
            : t("An error occurred while updating the web app"),
        );
        return;
      }
      toast.success(
        makePublic ? t("Web app is now public") : t("Web app is now private"),
      );
      clearCache();
      setIsOpen(false);
    } catch {
      toast.error(t("An error occurred while updating the web app"));
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <Button
        variant="white"
        leadingIcon={
          makePublic ? (
            <GlobeAltIcon className="h-4 w-4" />
          ) : (
            <LockClosedIcon className="h-4 w-4" />
          )
        }
        onClick={() => setIsOpen(true)}
      >
        {makePublic ? t("Make public") : t("Make private")}
      </Button>
      <Dialog open={isOpen} onClose={close} maxWidth="max-w-lg">
        <Dialog.Title onClose={close}>
          {makePublic
            ? t("Make this web app public?")
            : t("Make this web app private?")}
        </Dialog.Title>
        <Dialog.Content className="space-y-4 text-sm text-gray-600">
          {makePublic ? (
            <>
              <div className="flex gap-2 rounded-md bg-amber-50 p-3 text-amber-800">
                <ExclamationTriangleIcon className="h-5 w-5 shrink-0" />
                <p>
                  {t(
                    "Anyone with the link will be able to open this web app without an OpenHEXA account. You can make it private again at any time.",
                  )}
                </p>
              </div>
              {publicLink && (
                <div className="rounded-md bg-gray-50 p-3">
                  <p className="text-xs text-gray-500">{t("Public link")}</p>
                  <Clipboard value={publicLink}>
                    <code className="break-all text-gray-800">
                      {publicLink}
                    </code>
                  </Clipboard>
                </div>
              )}
              {isStatic && (
                <p>
                  {t(
                    "Public web apps can't call the OpenHEXA API yet, support is in the works. Until then, if this app loads workspace data or runs pipelines, it will stop working, and its API access settings will be hidden.",
                  )}
                </p>
              )}
            </>
          ) : (
            <p>
              {isStatic
                ? t(
                    "The public link will stop working: visitors without an OpenHEXA account will be asked to sign in. Workspace members keep access, and the app can call the OpenHEXA API again for the operations enabled under API access.",
                  )
                : t(
                    "The public link will stop working: visitors without an OpenHEXA account will be asked to sign in. Workspace members keep access.",
                  )}
            </p>
          )}
        </Dialog.Content>
        <Dialog.Actions>
          <Button variant="outlined" onClick={close} disabled={saving}>
            {t("Cancel")}
          </Button>
          <Button onClick={confirm} disabled={saving}>
            {makePublic ? t("Make public") : t("Make private")}
          </Button>
        </Dialog.Actions>
      </Dialog>
    </>
  );
};

WebappVisibilityButton.fragments = {
  webapp: gql`
    fragment WebappVisibilityButton_webapp on Webapp {
      id
      type
      isPublic
      url
      serveUrl
      permissions {
        update
      }
    }
  `,
};

export default WebappVisibilityButton;
