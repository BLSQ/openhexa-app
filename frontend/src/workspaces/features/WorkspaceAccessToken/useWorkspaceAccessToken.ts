import { useTranslation } from "next-i18next";
import { useState } from "react";
import { toast } from "react-toastify";
import { useGenerateWorkspaceTokenMutation } from "workspaces/graphql/mutations.generated";

type WorkspaceAccessToken = {
  // The token while it is shown, null while it is hidden or not fetched yet
  revealedToken: string | null;
  loading: boolean;
  toggle: () => Promise<void>;
};

/**
 * Reveals the access token of a workspace on demand.
 *
 * The token is fetched the first time it is asked for and kept afterwards:
 * hiding it does not throw it away, since asking for an identity token again
 * would issue a new one, and the one already revealed stays valid anyway.
 */
const useWorkspaceAccessToken = (
  workspaceSlug: string,
): WorkspaceAccessToken => {
  const { t } = useTranslation();
  const [token, setToken] = useState<string | null>(null);
  const [visible, setVisible] = useState(false);
  const [generateToken, { loading }] = useGenerateWorkspaceTokenMutation();

  const toggle = async () => {
    if (visible) {
      setVisible(false);
      return;
    }
    if (token) {
      setVisible(true);
      return;
    }

    const { data } = await generateToken({
      variables: { input: { slug: workspaceSlug } },
    });
    const result = data?.generateWorkspaceToken;
    if (!result?.success || !result.token) {
      toast.error(t("Failed to retrieve the access token"));
      return;
    }
    setToken(result.token);
    setVisible(true);
  };

  return { revealedToken: visible ? token : null, loading, toggle };
};

export default useWorkspaceAccessToken;
