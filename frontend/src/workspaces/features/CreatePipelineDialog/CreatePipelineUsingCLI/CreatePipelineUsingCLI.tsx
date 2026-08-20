import Link from "core/components/Link";
import Field from "core/components/forms/Field/Field";
import { Trans, useTranslation } from "next-i18next";
import { WorkspaceAccessTokenField } from "workspaces/features/WorkspaceAccessToken";
import { CreatePipelineDialog_WorkspaceFragment } from "../CreatePipelineDialog.generated";

type CreatePipelineUsingCLIProps = {
  open: boolean;
  workspace: CreatePipelineDialog_WorkspaceFragment;
};

const CreatePipelineUsingCLI = (props: CreatePipelineUsingCLIProps) => {
  const { t } = useTranslation();
  const { open, workspace } = props;

  return (
    <div className="space-y-4">
      <p className="mb-6">
        <Trans>
          In order to create pipelines, you need to setup the{" "}
          <code>openhexa</code> CLI using the{" "}
          <Link
            target="_blank"
            href="https://docs.openhexa.com/writing-pipelines/"
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
      <Field
        name="token"
        label={t("Access Token")}
        required
        description={
          <Trans>
            Your tokens for all workspaces are available in your{" "}
            <Link href="/user/account">account settings</Link>.
          </Trans>
        }
      >
        {/* The dialog stays mounted across open/close, so re-key the component
            to hide a previously revealed token when it is reopened. */}
        <WorkspaceAccessTokenField
          key={String(open)}
          workspaceSlug={workspace.slug}
          canGenerate={workspace.permissions.generateToken}
        />
      </Field>
    </div>
  );
};

export default CreatePipelineUsingCLI;
