import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import { useState } from "react";
import { useTranslation } from "next-i18next";
import { useGenerateNewDatabasePasswordMutation } from "workspaces/graphql/mutations.generated";
import { gql } from "@apollo/client";
import { GenerateWorkspaceDatabasePasswordDialog_WorkspaceFragment } from "./GenerateDatabasePasswordDialog.generated";
import { GenerateNewDatabasePasswordError } from "graphql/types";
import { ExclamationCircleIcon } from "@heroicons/react/24/outline";
import { toast } from "react-toastify";

type GenerateDatabasePasswordDialogProps = {
  onClose(): void;
  open: boolean;
  workspace: GenerateWorkspaceDatabasePasswordDialog_WorkspaceFragment;
};

const GenerateWorkspaceDatabasePasswordDialog = (
  props: GenerateDatabasePasswordDialogProps,
) => {
  const { open, onClose, workspace } = props;
  const { t } = useTranslation();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [generateNewPassword] = useGenerateNewDatabasePasswordMutation();
  const onSubmit = async () => {
    setIsSubmitting(true);
    const { data } = await generateNewPassword({
      variables: {
        input: {
          workspaceSlug: workspace.slug,
        },
      },
    });

    if (!data?.generateNewDatabasePassword) {
      throw new Error("Unknown error.");
    }

    if (data.generateNewDatabasePassword.success) {
      toast.info(t("Password successfully changed"));
      onClose();
      setIsSubmitting(false);
    }
    if (
      data.generateNewDatabasePassword.errors.includes(
        GenerateNewDatabasePasswordError.PermissionDenied,
      )
    ) {
      throw new Error("You are not authorized to perform this action");
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <Dialog.Title>{t("Regenerate database password")}</Dialog.Title>
      <Dialog.Content className="space-y-2 py-2">
        <p>{t("You are about to replace the workspace database password.")}</p>
        <p>
          <ExclamationCircleIcon className="inline-block h-6 w-6 text-amber-400" />
          {t("This action cannot be undone.")}
        </p>
        <p>{t("After regenerating the password, you will have to:")}</p>
        <ul className="list list-inside list-disc">
          <li>{t("Restart all opened notebooks")}</li>
          <li>
            {t(
              "Update connection parameters in 3rd-party tools (visualization & BI tools, other data systems...)",
            )}
          </li>
        </ul>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button onClick={onSubmit}>
          {isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Replace password")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

GenerateWorkspaceDatabasePasswordDialog.fragments = {
  workspace: gql`
    fragment GenerateWorkspaceDatabasePasswordDialog_workspace on Workspace {
      slug
    }
  `,
};

export default GenerateWorkspaceDatabasePasswordDialog;
