import { gql, useMutation } from "@apollo/client";
import Button from "core/components/Button/Button";
import Link from "core/components/Link";
import Field from "core/components/forms/Field/Field";
import Textarea from "core/components/forms/Textarea/Textarea";
import { Trans, useTranslation } from "next-i18next";
import { useEffect, useState } from "react";
import { CreatePipelineDialog_WorkspaceFragment } from "../CreatePipelineDialog.generated";
import { GenerateWorkspaceTokenMutation } from "./CreatePipelineUsingCLI.generated";

type CreatePipelineUsingCLIProps = {
  open: boolean;
  workspace: CreatePipelineDialog_WorkspaceFragment;
};

const CreatePipelineUsingCLI = (props: CreatePipelineUsingCLIProps) => {
  const { t } = useTranslation();
  const { open, workspace } = props;

  const [token, setToken] = useState<null | string>(null);
  const [generateToken] = useMutation<GenerateWorkspaceTokenMutation>(
    gql`
      mutation GenerateWorkspaceToken($input: GenerateWorkspaceTokenInput!) {
        generateWorkspaceToken(input: $input) {
          token
          success
        }
      }
    `,
    { variables: { input: { slug: workspace.slug } } },
  );

  const onTokenClick = async () => {
    if (!token) {
      const { data } = await generateToken();
      setToken(data?.generateWorkspaceToken?.token ?? null);
    }
  };

  useEffect(() => {
    if (open) {
      setToken(null);
    }
  }, [open]);

  return (
    <div className="space-y-4">
      <p className="mb-6">
        <Trans>
          In order to create pipelines, you need to setup the{" "}
          <code>openhexa</code> CLI using the{" "}
          <Link
            target="_blank"
            href="https://github.com/BLSQ/openhexa/wiki/Writing-OpenHexa-pipelines"
          >
            guide
          </Link>{" "}
          on Github.
        </Trans>
      </p>
      <p>
        {t(
          "Configure the workspace in your terminal using the following commands:",
        )}
      </p>

      <pre className=" bg-slate-100 p-2 font-mono text-sm leading-6">
        <div>
          <span className="select-none text-gray-400">$ </span>pip install
          openhexa.sdk
          <span className="select-none text-gray-400">
            {t("# if not installed")}
          </span>
        </div>
        <div>
          <span className="select-none text-gray-400">$ </span>
          <span className="whitespace-normal">
            openhexa workspaces add <b>{workspace.slug}</b>
          </span>
        </div>
      </pre>
      <Field name="token" label={t("Access Token")} required>
        <div className="flex w-full flex-1 items-center gap-1">
          {token ? (
            <Textarea className="font-mono" value={token} readOnly />
          ) : (
            <Button variant="secondary" onClick={onTokenClick}>
              {t("Show")}
            </Button>
          )}
        </div>
      </Field>
    </div>
  )
}

export default CreatePipelineUsingCLI;
