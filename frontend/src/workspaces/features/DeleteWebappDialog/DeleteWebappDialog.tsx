import { gql } from "@apollo/client";
import { Trans, useTranslation } from "react-i18next";
import { useRouter } from "next/router";
import Button from "core/components/Button";
import Spinner from "core/components/Spinner";
import { DeleteWebappError } from "graphql/types";
import { useState } from "react";
import Dialog from "core/components/Dialog";
import {
  WebappDelete_WebappFragment,
  WebappDelete_WorkspaceFragment,
} from "./DeleteWebappDialog.generated";
import useCacheKey from "core/hooks/useCacheKey";
import { toast } from "react-toastify";
import { useMutation } from "@apollo/client/react";
import { graphql } from "graphql/gql";

const DeleteWebappDoc = graphql(`
mutation deleteWebapp($input: DeleteWebappInput!) {
  deleteWebapp(input: $input) {
    success
    errors
  }
}
`);

type DeleteWebappDialogProps = {
  open: boolean;
  onClose: () => void;
  webapp: WebappDelete_WebappFragment;
  workspace: WebappDelete_WorkspaceFragment;
};

const DeleteWebappDialog = (props: DeleteWebappDialogProps) => {
  const { t } = useTranslation();
  const { open, onClose, webapp, workspace } = props;
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const clearCache = useCacheKey("webapps");

  const [deleteWebapp] = useMutation(DeleteWebappDoc);

  const onSubmit = async () => {
    setIsSubmitting(true);
    const { data } = await deleteWebapp({
      variables: {
        input: {
          id: webapp.id,
        },
      },
    });

    if (!data?.deleteWebapp) {
      throw new Error("Unknown error.");
    }

    setIsSubmitting(false);
    if (data.deleteWebapp.success) {
      toast.success(t("Webapp deleted successfully."));
      clearCache();
      router.push({
        pathname: "/workspaces/[workspaceSlug]/webapps",
        query: { workspaceSlug: workspace.slug },
      });
    } else if (
      data.deleteWebapp.errors.includes(DeleteWebappError.PermissionDenied)
    ) {
      toast.error(t("Missing permissions to delete the webapp."));
    } else {
      toast.error(t("Failed to delete the webapp."));
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <Dialog.Title>{t("Delete webapp")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <p>
          <Trans>
            Are you sure you want to delete web app <b>{webapp.name}</b> ?
          </Trans>
        </p>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button onClick={onSubmit}>
          {isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Delete")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

DeleteWebappDialog.fragment = {
  webapp: gql`
    fragment WebappDelete_webapp on Webapp {
      id
      name
    }
  `,
  workspace: gql`
    fragment WebappDelete_workspace on Workspace {
      slug
    }
  `,
};

export default DeleteWebappDialog;
