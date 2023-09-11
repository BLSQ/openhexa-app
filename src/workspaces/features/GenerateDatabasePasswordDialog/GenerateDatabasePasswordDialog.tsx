import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useGenerateNewDatabasePasswordMutation } from "workspaces/graphql/mutations.generated";
import { gql } from "@apollo/client";
import { GenerateWorkspaceDatabasePasswordDialog_WorkspaceFragment } from "./GenerateDatabasePasswordDialog.generated";
import { GenerateNewDatabasePasswordError } from "graphql-types";
import { AlertType, displayAlert } from "core/helpers/alert";

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
      displayAlert(t("Password successfully changed"), AlertType.info);
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
      <Dialog.Content className="space-y-4">
        <p>
          {t(
            "You're about to generate a new password for the workspace database. This action cannot be undone. Make sure to:",
          )}
        </p>
        <ul className="list list-inside list-disc">
          <li>{t("Restart all opened notebooks")}</li>
          <li>{t("Update external tools credentials")}</li>
        </ul>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" type="button" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button onClick={onSubmit}>
          {isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Generate")}
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
