import { gql } from "@apollo/client";
import Clipboard from "core/components/Clipboard";
import ShareButton from "core/features/Sharing/ShareButton";
import {
  SHARING_STYLES,
  SharingOption,
} from "core/features/Sharing/sharingStyles";
import useCacheKey from "core/hooks/useCacheKey";
import { UpdateWebappError, WebappType } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useMemo } from "react";
import { toast } from "react-toastify";
import { useUpdateWebappMutation } from "webapps/graphql/mutations.generated";
import { WebappVisibilityButton_WebappFragment } from "./WebappVisibilityButton.generated";

// Web apps only know public or not; these mirror the shared sharing levels.
const PRIVATE = "private";
const PUBLIC = "public";
type WebappSharing = typeof PRIVATE | typeof PUBLIC;

type WebappVisibilityButtonProps = {
  webapp: WebappVisibilityButton_WebappFragment;
};

const WebappVisibilityButton = ({ webapp }: WebappVisibilityButtonProps) => {
  const { t } = useTranslation();
  const [updateWebapp] = useUpdateWebappMutation();
  const clearCache = useCacheKey("webapps");
  const options = useMemo(
    (): SharingOption<WebappSharing>[] => [
      {
        value: PRIVATE,
        label: t("Private"),
        description: t("Only workspace members can open it."),
        ...SHARING_STYLES.private,
      },
      {
        value: PUBLIC,
        label: t("Public"),
        description: t(
          "Anyone with the link can open it, even without an OpenHEXA account.",
        ),
        ...SHARING_STYLES.public,
      },
    ],
    [t],
  );

  if (!webapp.permissions.update) {
    return null;
  }

  // Only static apps call the OpenHEXA API (through their proxy, which serves
  // public apps anonymously), so the API consequences only apply to them.
  const isStatic = webapp.type === WebappType.Static;
  const publicLink = webapp.serveUrl ?? webapp.url;

  const save = async (next: WebappSharing) => {
    const makePublic = next === PUBLIC;
    let errorMessage = t("An error occurred while updating the web app");
    try {
      const { data } = await updateWebapp({
        variables: { input: { id: webapp.id, isPublic: makePublic } },
      });
      if (!data?.updateWebapp?.errors?.length) {
        toast.success(
          makePublic ? t("Web app is now public") : t("Web app is now private"),
        );
        clearCache();
        return;
      }
      if (data.updateWebapp.errors[0] === UpdateWebappError.PermissionDenied) {
        errorMessage = t("You do not have permission to update this web app");
      }
    } catch {}
    toast.error(errorMessage);
    throw new Error(errorMessage);
  };

  return (
    <ShareButton
      options={options}
      value={webapp.isPublic ? PUBLIC : PRIVATE}
      onSave={save}
      warning={(next, from) =>
        next === PUBLIC &&
        from === PRIVATE &&
        t(
          "Anyone with the link will be able to open this web app without an OpenHEXA account. You can make it private again at any time.",
        )
      }
    >
      {(next, from) =>
        next === from ? null : next === PUBLIC ? (
          <>
            {publicLink && (
              <div className="rounded-md bg-gray-50 p-3">
                <p className="text-xs text-gray-500">{t("Public link")}</p>
                <Clipboard value={publicLink}>
                  <code className="break-all text-gray-800">{publicLink}</code>
                </Clipboard>
              </div>
            )}
            {isStatic && (
              <p>
                {t(
                  "Visitors won't have an account, so the app will only reach the workspace's public resources through the OpenHEXA API, and its API access settings will no longer apply. Anything else it loads or runs will stop working.",
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
        )
      }
    </ShareButton>
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
