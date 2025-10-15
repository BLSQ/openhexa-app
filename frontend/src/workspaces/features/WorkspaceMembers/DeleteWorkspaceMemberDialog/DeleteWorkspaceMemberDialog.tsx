import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import { useState } from "react";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useDeleteWorkspaceMemberMutation } from "workspaces/graphql/mutations.generated";
import useCacheKey from "core/hooks/useCacheKey";
import {
  DeleteWorkspaceMemberError,
  OrganizationMembershipRole,
} from "graphql/types";
import useMe from "identity/hooks/useMe";
import { gql } from "@apollo/client";
import { DeleteWorkspaceMember_WorkspaceMemberFragment } from "./DeleteWorkspaceMemberDialog.generated";
import { ExclamationTriangleIcon } from "@heroicons/react/24/outline";

type DeleteWorkspaceMemberProps = {
  onClose(): void;
  open: boolean;
  member: DeleteWorkspaceMember_WorkspaceMemberFragment;
};

const DeleteWorkspaceMemberDialog = (props: DeleteWorkspaceMemberProps) => {
  const router = useRouter();
  const me = useMe();
  const { t } = useTranslation();
  const { open, onClose, member } = props;

  const [isSubmitting, setIsSubmitting] = useState(false);

  const [deleteWorkspaceMember] = useDeleteWorkspaceMemberMutation();
  const clearCache = useCacheKey("workspace");

  const onSubmit = async () => {
    setIsSubmitting(true);
    const { data } = await deleteWorkspaceMember({
      variables: {
        input: {
          membershipId: member.id,
        },
      },
    });

    if (!data?.deleteWorkspaceMember) {
      throw new Error("Unknown error.");
    }

    if (data.deleteWorkspaceMember.success) {
      clearCache();
      setIsSubmitting(false);
      if (me.user?.id === member.user.id) {
        await router.push("/workspaces");
      }
      onClose();
    }

    if (
      data.deleteWorkspaceMember.errors.includes(
        DeleteWorkspaceMemberError.PermissionDenied,
      )
    ) {
      throw new Error("You are not authorized to perform this action");
    }
  };

  const orgRoleLabel =
    member.organizationMembership?.role === OrganizationMembershipRole.Owner
      ? t("Owner")
      : member.organizationMembership?.role === OrganizationMembershipRole.Admin
        ? t("Admin")
        : "";

  return (
    <Dialog open={open} onClose={onClose}>
      <Dialog.Title>
        {t("Remove member", {
          name: member.user.displayName,
        })}
      </Dialog.Title>
      <Dialog.Content className="space-y-4">
        <p>
          {t("You're about to remove {{name}} from this workspace.", {
            name: member.user.displayName,
          })}
        </p>
        {orgRoleLabel && (
          <div className="flex gap-2 rounded-md bg-yellow-50 p-3 border border-yellow-200">
            <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-yellow-800">
              {t(
                "This user is an organization {{role}} and will still be able to access this workspace even after being removed from the workspace members list.",
                { role: orgRoleLabel },
              )}
            </p>
          </div>
        )}
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

DeleteWorkspaceMemberDialog.fragments = {
  member: gql`
    fragment DeleteWorkspaceMember_workspaceMember on WorkspaceMembership {
      id
      user {
        id
        displayName
      }
      organizationMembership {
        role
      }
    }
  `,
};

export default DeleteWorkspaceMemberDialog;
