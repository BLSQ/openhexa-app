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
};

const WorkspaceAccessToken = (props: WorkspaceAccessTokenProps) => {
  const { workspaceSlug, canGenerate } = props;
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

  if (!token) {
    return (
      <Button variant="secondary" onClick={onShowClick} disabled={loading}>
        {t("Show")}
      </Button>
    );
  }

  return (
    <Input
      name="token"
      value={token}
      readOnly
      fullWidth
      onFocus={(event) => event.target.select()}
      classNameOverrides="font-mono text-xs"
      trailingIcon={<Clipboard value={token} />}
    />
  );
};

export default WorkspaceAccessToken;
