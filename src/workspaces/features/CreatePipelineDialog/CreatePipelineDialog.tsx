import { gql, useMutation } from "@apollo/client";
import Button from "core/components/Button/Button";
import Dialog from "core/components/Dialog";
import Link from "core/components/Link";
import Field from "core/components/forms/Field/Field";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  CreatePipelineDialog_WorkspaceFragment,
  GenerateWorkspaceTokenMutation,
} from "./CreatePipelineDialog.generated";
import Textarea from "core/components/forms/Textarea/Textarea";

type CreatePipelineDialogProps = {
  open: boolean;
  onClose: () => void;
  workspace: CreatePipelineDialog_WorkspaceFragment;
};

const CreatePipelineDialog = (props: CreatePipelineDialogProps) => {
  const { open, onClose, workspace } = props;
  const { t } = useTranslation();
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
    <Dialog open={open} onClose={onClose} maxWidth="max-w-2xl">
      <Dialog.Title>{t("How to create a pipeline")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <p className="mb-6">
          In order to create pipelines, you need to setup the{" "}
          <code>openhexa</code> CLI using the{" "}
          <Link
            target="_blank"
            href="https://github.com/BLSQ/openhexa/wiki/Writing-OpenHexa-pipelines"
          >
            guide
          </Link>{" "}
          on Github.
        </p>
        <p>
          Configure the workspace in your terminal using the following commands:
        </p>

        <pre className=" bg-slate-100 p-2 font-mono text-sm leading-6">
          <div>
            <span className="select-none text-gray-400">$ </span>pip install
            openhexa.sdk{" "}
            <span className="select-none text-gray-400">
              # if not installed
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
      </Dialog.Content>
      <Dialog.Actions>
        <Button onClick={onClose}>{t("Close")}</Button>
      </Dialog.Actions>
    </Dialog>
  );
};

CreatePipelineDialog.fragments = {
  workspace: gql`
    fragment CreatePipelineDialog_workspace on Workspace {
      slug
    }
  `,
};

export default CreatePipelineDialog;
