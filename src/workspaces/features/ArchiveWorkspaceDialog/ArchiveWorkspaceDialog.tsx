import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useRouter } from "next/router";
import { useArchiveWorkspaceMutation } from "workspaces/graphql/mutations.generated";
import useCacheKey from "core/hooks/useCacheKey";
import { gql } from "@apollo/client";
import { ArchiveWorkspaceError } from "graphql-types";
import { ArchiveWorkspace_WorkspaceFragment } from "./ArchiveWorkspaceDialog.generated";

type ArchiveWorkspaceDialogProps = {
  onClose(): void;
  open: boolean;
  workspace: ArchiveWorkspace_WorkspaceFragment;
};

const ArchiveWorkspaceDialog = (props: ArchiveWorkspaceDialogProps) => {
  const router = useRouter();
  const { t } = useTranslation();
  const { open, onClose, workspace } = props;
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [archiveWorkspace] = useArchiveWorkspaceMutation();
  const clearCache = useCacheKey(["workspaces", workspace.slug]);

  const onSubmit = async () => {
    setIsSubmitting(true);
    const { data } = await archiveWorkspace({
      variables: {
        input: {
          slug: workspace.slug,
        },
      },
    });

    if (!data?.archiveWorkspace) {
      throw new Error("Unknown error.");
    }

    if (data.archiveWorkspace.success) {
      clearCache();
      setIsSubmitting(false);
      await router.push("/workspaces");
    }
    if (
      data.archiveWorkspace.errors.includes(
        ArchiveWorkspaceError.PermissionDenied
      )
    ) {
      throw new Error("You are not authorized to perform this action");
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <Dialog.Title>
        {t("Archive {{name}}", { name: workspace.name })}
      </Dialog.Title>
      <Dialog.Content className="space-y-4">
        <p>
          {t("You're about to archive this workspace and all its content.")}
        </p>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" type="button" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button onClick={onSubmit}>
          {isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Archive")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

ArchiveWorkspaceDialog.fragments = {
  workspace: gql`
    fragment ArchiveWorkspace_workspace on Workspace {
      slug
      name
    }
  `,
};

export default ArchiveWorkspaceDialog;
