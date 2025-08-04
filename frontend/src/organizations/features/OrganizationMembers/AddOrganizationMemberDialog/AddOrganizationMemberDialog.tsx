import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import Spinner from "core/components/Spinner";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "core/components/Table";
import { useTranslation } from "next-i18next";
import useForm from "core/hooks/useForm";
import {
  InviteOrganizationMemberError,
  OrganizationMembershipRole, WorkspaceInvitationInput,
  WorkspaceMembershipRole
} from "graphql/types";
import SimpleSelect from "core/components/forms/SimpleSelect";
import React, { ComponentProps, useEffect, useState } from "react";
import { useInviteOrganizationMemberMutation } from "organizations/features/OrganizationMembers/OrganizationMembers.generated";
import { UserPicker } from "workspaces/features/UserPicker/UserPicker";
import { OrganizationQuery } from "organizations/graphql/queries.generated";
import { formatOrganizationMembershipRole } from "organizations/helpers/organization";
import SearchInput from "core/features/SearchInput";

type AddOrganizationMemberDialogProps = {
  onClose(): void;
  open: boolean;
  organization: OrganizationQuery["organization"];
};

type Form = {
  user: ComponentProps<typeof UserPicker>["value"];
  organizationRole: OrganizationMembershipRole;
  workspaceInvitations: WorkspaceInvitationInput[]
};

const getDefaultWorkspaceRole = (
  orgRole: OrganizationMembershipRole,
): WorkspaceMembershipRole => {
  switch (orgRole) {
    case OrganizationMembershipRole.Admin:
      return WorkspaceMembershipRole.Editor;
    case OrganizationMembershipRole.Owner:
      return WorkspaceMembershipRole.Admin;
    case OrganizationMembershipRole.Member:
    default:
      return WorkspaceMembershipRole.Viewer;
  }
};

const AddOrganizationMemberDialog = (
  props: AddOrganizationMemberDialogProps,
) => {
  const { t } = useTranslation();
  const { open, onClose, organization } = props;

  const [inviteOrganizationMember] = useInviteOrganizationMemberMutation({
    refetchQueries: ["OrganizationMembers", "GetUsers", "Organization", "OrganizationInvitations"],
  });

  const [searchTerm, setSearchTerm] = useState("");
  const [workspaceInvitations, setWorkspaceInvitations] = useState<
    WorkspaceInvitationInput[]
  >([]);
  const [manuallyEditedWorkspaces, setManuallyEditedWorkspaces] = useState<
    Set<string>
  >(new Set());

  const form = useForm<Form>({
    onSubmit: async (values) => {
      const { data } = await inviteOrganizationMember({
        variables: {
          input: {
            userEmail: values.user!.email,
            organizationId: organization?.id!,
            organizationRole: values.organizationRole,
            workspaceInvitations,
          },
        },
      });

      if (!data?.inviteOrganizationMember) {
        throw new Error("Unknown error.");
      }

      const errors = data.inviteOrganizationMember.errors;
      if (errors.includes(InviteOrganizationMemberError.PermissionDenied)) {
        throw new Error("You are not authorized to perform this action");
      }
      if (errors.includes(InviteOrganizationMemberError.WorkspaceNotFound)) {
        throw new Error("One or more workspaces were not found");
      }
      if (errors.includes(InviteOrganizationMemberError.AlreadyMember)) {
        throw new Error(
          "User is already a member of this organization or invited to it",
        );
      }
      if (errors.length > 0) {
        throw new Error("An error occurred while inviting the member.");
      }

      onClose();
    },
    initialState: {
      user: null,
      organizationRole: OrganizationMembershipRole.Member,
      workspaceInvitations: [],
    },
    validate: (values) => {
      const errors = {} as any;
      if (!values.user) {
        errors.user = t("User is required");
      }
      if (!values.organizationRole) {
        errors.organizationRole = t("Organization role is mandatory");
      }
      return errors;
    },
  });

  useEffect(() => {
    if (open && organization?.workspaces?.items) {
      form.resetForm();
      setSearchTerm("");
      setManuallyEditedWorkspaces(new Set());

      const orgRole =
        form.formData.organizationRole || OrganizationMembershipRole.Member;
      const defaultRole = getDefaultWorkspaceRole(orgRole);
      const initialWorkspaceInvitations = organization.workspaces.items.map(
        (workspace) => ({
          workspaceSlug: workspace.slug,
          workspaceName: workspace.name,
          role: defaultRole,
        }),
      );
      setWorkspaceInvitations(initialWorkspaceInvitations);
    }
  }, [open, form, organization?.workspaces]);

  useEffect(() => {
    if (!organization?.workspaces?.items || !form.formData.organizationRole)
      return;

    const defaultRole = getDefaultWorkspaceRole(form.formData.organizationRole);

    setWorkspaceInvitations((prev) =>
      prev.map((invitation) => {
        if (manuallyEditedWorkspaces.has(invitation.workspaceSlug)) {
          return invitation;
        }
        return { ...invitation, role: defaultRole };
      }),
    );
  }, [
    form.formData.organizationRole,
    organization?.workspaces?.items,
  ]);

  const handleRoleChange = (
    workspaceSlug: string,
    workspaceName: string,
    role: WorkspaceMembershipRole | "NONE",
  ) => {
    setManuallyEditedWorkspaces((prev) => new Set(prev).add(workspaceSlug));

    setWorkspaceInvitations((prev) => {
      const filtered = prev.filter(
        (inv) => inv.workspaceSlug !== workspaceSlug,
      );
      return role === "NONE"
        ? filtered
        : [...filtered, { workspaceSlug, workspaceName, role }];
    });
  };

  const filteredWorkspaces =
    organization?.workspaces?.items?.filter((workspace) =>
      workspace.name.toLowerCase().includes(searchTerm.toLowerCase()),
    ) || [];

  return (
    <Dialog open={open} onClose={onClose} onSubmit={form.handleSubmit}>
      <Dialog.Title>{t("Invite Member")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <Field
          name="user-picker"
          label={t("User")}
          required
          error={form.errors.user}
        >
          <UserPicker
            id="user-picker"
            value={form.formData.user!}
            onChange={(user) => form.setFieldValue("user", user)}
            organizationId={organization?.id}
          />
        </Field>
        <Field name="organizationRole" label={t("Organization Role")} required>
          <SimpleSelect
            id="organizationRole"
            name="organizationRole"
            value={form.formData.organizationRole}
            onChange={form.handleInputChange}
            required
          >
            {Object.values(OrganizationMembershipRole).map((role) => (
              <option key={role} value={role}>
                {formatOrganizationMembershipRole(role)}
              </option>
            ))}
          </SimpleSelect>
        </Field>

        <Field name="workspaces" label={t("Workspaces")} required>
          <div className="space-y-3">
            <SearchInput
              name="workspaces"
              placeholder={t("Search workspaces...")}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />

            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <div className="max-h-64 overflow-y-auto">
                <Table className="table-fixed">
                  <TableHead>
                    <TableRow>
                      <TableCell heading className="w-1/2"></TableCell>
                      <TableCell heading className="text-center w-1/8">
                        {t("Admin")}
                      </TableCell>
                      <TableCell heading className="text-center w-1/8">
                        {t("Editor")}
                      </TableCell>
                      <TableCell heading className="text-center w-1/8">
                        {t("Viewer")}
                      </TableCell>
                      <TableCell heading className="text-center w-1/8">
                        {t("None")}
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredWorkspaces.length === 0 ? (
                      <TableRow>
                        <TableCell
                          className="text-center py-8 text-gray-500"
                          colSpan={5}
                        >
                          <p className="text-sm">
                            {searchTerm
                              ? t("No workspace found")
                              : t("No workspace available")}
                          </p>
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredWorkspaces.map((workspace) => {
                        const invitation = workspaceInvitations.find(
                          (inv) => inv.workspaceSlug === workspace.slug,
                        );
                        const currentRole =
                          invitation?.role || ("NONE" as const);

                        return (
                          <TableRow key={workspace.slug}>
                            <TableCell
                              className="truncate font-medium max-w-0"
                              title={workspace.name}
                            >
                              {workspace.name}
                            </TableCell>

                            {[
                              ...Object.values(WorkspaceMembershipRole),
                              "NONE" as const,
                            ].map((role) => (
                              <TableCell
                                key={workspace.slug + role}
                                className="text-center"
                              >
                                <input
                                  type="radio"
                                  name={`workspace-${workspace.slug}-${role}`}
                                  checked={currentRole === role}
                                  onChange={() =>
                                    handleRoleChange(workspace.slug, workspace.name, role)
                                  }
                                  className="h-4 w-4 text-blue-600 cursor-pointer"
                                />
                              </TableCell>
                            ))}
                          </TableRow>
                        );
                      })
                    )}
                  </TableBody>
                </Table>
              </div>
            </div>
          </div>
        </Field>

        {form.submitError && (
          <div className="text-danger mt-3 text-sm">{form.submitError}</div>
        )}
      </Dialog.Content>
      <Dialog.Actions>
        <Button onClick={onClose} variant="white">
          {t("Cancel")}
        </Button>
        <Button type="submit" disabled={form.isSubmitting}>
          {form.isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Invite Member")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default AddOrganizationMemberDialog;
