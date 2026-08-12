import Button from "core/components/Button";
import Clipboard from "core/components/Clipboard";
import Input from "core/components/forms/Input";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import { toast } from "react-toastify";
import { useGenerateWorkspaceTokenMutation } from "workspaces/graphql/mutations.generated";

type WorkspaceAccessTokenProps = {
  workspaceSlug: string;
  canGenerate: boolean;
  // Users without a membership get an identity token, which expires. Flagging it
  // keeps them from pasting a token that stops working the next day.
  temporary?: boolean;
};

const WorkspaceAccessToken = (props: WorkspaceAccessTokenProps) => {
  const { workspaceSlug, canGenerate, temporary = false } = props;
  const { t } = useTranslation();

  const [token, setToken] = useState<string | null>(null);
  const [generateToken, { loading }] = useGenerateWorkspaceTokenMutation();

  const onShowClick = async () => {
    const { data } = await generateToken({
      variables: { input: { slug: workspaceSlug } },
    });
    const result = data?.generateWorkspaceToken;
    if (!result?.success || !result.token) {
      toast.error(t("Failed to retrieve the access token"));
      return;
    }
    setToken(result.token);
  };

  if (!canGenerate) {
    return (
      <span className="text-sm italic text-gray-500">
        {t("Not available for viewers")}
      </span>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {token ? (
        <Input
          name="token"
          value={token}
          readOnly
          fullWidth
          onFocus={(event) => event.target.select()}
          classNameOverrides="font-mono text-xs"
          trailingIcon={<Clipboard value={token} />}
        />
      ) : (
        <Button variant="secondary" onClick={onShowClick} disabled={loading}>
          {t("Show")}
        </Button>
      )}
      {temporary && (
        <span
          className="shrink-0 text-xs italic text-gray-500"
          title={t(
            "You are not a member of this workspace, so its token expires and has to be generated again.",
          )}
        >
          {t("Temporary")}
        </span>
      )}
    </div>
  );
};

export default WorkspaceAccessToken;
