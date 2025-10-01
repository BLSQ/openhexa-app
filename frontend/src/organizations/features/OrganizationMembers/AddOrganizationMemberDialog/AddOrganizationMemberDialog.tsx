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
  OrganizationMembershipRole,
  WorkspaceInvitationInput,
  WorkspaceMembershipRole,
} from "graphql/types";
import SimpleSelect from "core/components/forms/SimpleSelect";
import React, { useEffect, useState } from "react";
import { useInviteOrganizationMemberMutation } from "organizations/features/OrganizationMembers/OrganizationMembers.generated";
import Input from "core/components/forms/Input";
import { OrganizationQuery } from "organizations/graphql/queries.generated";
import { formatOrganizationMembershipRole } from "organizations/helpers/organization";
import { formatWorkspaceMembershipRole } from "workspaces/helpers/workspace";
import SearchInput from "core/features/SearchInput";
import { toast } from "react-toastify";

type AddOrganizationMemberDialogProps = {
  onClose(): void;
  open: boolean;
  organization: OrganizationQuery["organization"];
};

type Form = {
  email: string;
  organizationRole: OrganizationMembershipRole;
  workspaceInvitations: WorkspaceInvitationInput[];
};

const getDefaultWorkspaceRole = (
  orgRole: OrganizationMembershipRole,
): WorkspaceRole => {
  switch (orgRole) {
    case OrganizationMembershipRole.Admin:
      return WorkspaceMembershipRole.Admin;
    case OrganizationMembershipRole.Owner:
      return WorkspaceMembershipRole.Admin;
    case OrganizationMembershipRole.Member:
    default:
      return WORKSPACE_ROLE_NONE;
  }
};

const WORKSPACE_ROLE_NONE = "NONE" as const;
type WORKSPACE_ROLE_NONE = typeof WORKSPACE_ROLE_NONE;
type WorkspaceRole = WorkspaceMembershipRole | WORKSPACE_ROLE_NONE;
const buildInvitations = (
  workspaces: { slug: string; name: string }[],
  role: WorkspaceRole,
): WorkspaceInvitationInput[] => {
  if (role === WORKSPACE_ROLE_NONE) return [];

  return workspaces.map((workspace) => ({
    workspaceSlug: workspace.slug,
    workspaceName: workspace.name,
    role: role as WorkspaceMembershipRole,
  }));
};

const AddOrganizationMemberDialog = (
  props: AddOrganizationMemberDialogProps,
) => {
  const { t } = useTranslation();
  const { open, onClose, organization } = props;

  const [inviteOrganizationMember] = useInviteOrganizationMemberMutation({
    refetchQueries: [
      "OrganizationMembers",
      "Organization",
      "OrganizationInvitations",
    ],
  });

  const [searchTerm, setSearchTerm] = useState("");
  const [bulkRoleSelection, setBulkRoleSelection] =
    useState<WorkspaceRole>(WORKSPACE_ROLE_NONE);

  const form = useForm<Form>({
    onSubmit: async (values) => {
      const { data } = await inviteOrganizationMember({
        variables: {
          input: {
            userEmail: values.email,
            organizationId: organization?.id!,
            organizationRole: values.organizationRole,
            workspaceInvitations: values.workspaceInvitations,
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
      toast.success(t("Invitation sent!"));
      onClose();
    },
    initialState: {
      email: "",
      organizationRole: OrganizationMembershipRole.Member,
      workspaceInvitations: [],
    },
    validate: (values) => {
      const errors = {} as any;
      if (!values.email) {
        errors.email = t("Email address is mandatory");
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

      const orgRole =
        form.formData.organizationRole || OrganizationMembershipRole.Member;
      const defaultRole = getDefaultWorkspaceRole(orgRole);
      setBulkRoleSelection(defaultRole);
      const initialWorkspaceInvitations = buildInvitations(
        organization.workspaces.items,
        defaultRole,
      );
      form.setFieldValue("workspaceInvitations", initialWorkspaceInvitations);
    }
  }, [open, organization?.workspaces]);

  useEffect(() => {
    if (!organization?.workspaces?.items || !form.formData.organizationRole)
      return;

    const defaultRole = getDefaultWorkspaceRole(form.formData.organizationRole);
    setBulkRoleSelection(defaultRole);

    const updatedInvitations = buildInvitations(
      organization.workspaces.items,
      defaultRole,
    );
    form.setFieldValue("workspaceInvitations", updatedInvitations);
  }, [form.formData.organizationRole, organization?.workspaces?.items]);

  const handleRoleChange = (
    workspaceSlug: string,
    workspaceName: string,
    role: WorkspaceRole,
  ) => {
    const currentInvitations = form.formData.workspaceInvitations || [];
    const filtered = currentInvitations.filter(
      (inv) => inv.workspaceSlug !== workspaceSlug,
    );
    const updatedInvitations =
      role === WORKSPACE_ROLE_NONE
        ? filtered
        : [...filtered, { workspaceSlug, workspaceName, role }];

    form.setFieldValue("workspaceInvitations", updatedInvitations);
  };

  const handleBulkRoleChange = (role: WorkspaceRole) => {
    if (!organization?.workspaces?.items) return;

    setBulkRoleSelection(role);

    const updatedInvitations = buildInvitations(
      organization.workspaces.items,
      role,
    );

    form.setFieldValue("workspaceInvitations", updatedInvitations);
  };

  const filteredWorkspaces =
    organization?.workspaces?.items?.filter((workspace) =>
      workspace.name.toLowerCase().includes(searchTerm.toLowerCase()),
    ) || [];

  return (
    <Dialog
      open={open}
      onClose={onClose}
      onSubmit={form.handleSubmit}
      maxWidth="max-w-4xl"
    >
      <Dialog.Title>{t("Invite Member")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <Field
          name="email"
          label={t("User")}
          required
          error={form.errors.email}
        >
          <Input
            id="email"
            name="email"
            type="email"
            placeholder={t("Enter email address")}
            value={form.formData.email}
            onChange={form.handleInputChange}
            className="w-full"
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
            {[
              OrganizationMembershipRole.Owner,
              OrganizationMembershipRole.Admin,
              OrganizationMembershipRole.Member,
            ]
              .filter(
                (role) =>
                  role !== OrganizationMembershipRole.Owner ||
                  organization?.permissions.manageOwners,
              )
              .map((role) => (
                <option key={role} value={role}>
                  {formatOrganizationMembershipRole(role)}
                </option>
              ))}
          </SimpleSelect>
        </Field>

        <Field name="bulkRole" label={t("Role for all workspaces")} required>
          <SimpleSelect
            id="bulkRole"
            value={bulkRoleSelection}
            onChange={(e) =>
              handleBulkRoleChange(e.target.value as WorkspaceRole)
            }
            className="w-full"
            required
          >
            {Object.values(WorkspaceMembershipRole).map((role) => (
              <option key={role} value={role}>
                {formatWorkspaceMembershipRole(role)}
              </option>
            ))}
            <option value={WORKSPACE_ROLE_NONE}>{t("None")}</option>
          </SimpleSelect>
        </Field>
        <Field name="workspaces" label={t("Workspaces")} required>
          <div className="space-y-3">
            <SearchInput
              name="workspaces"
              placeholder={t("Search workspaces...")}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full"
            />

            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <div className="max-h-64 overflow-y-auto">
                <Table className="w-full">
                  <TableHead>
                    <TableRow>
                      <TableCell heading></TableCell>
                      <TableCell heading className="text-center w-24">
                        {t("Admin")}
                      </TableCell>
                      <TableCell heading className="text-center w-24">
                        {t("Editor")}
                      </TableCell>
                      <TableCell heading className="text-center w-24">
                        {t("Viewer")}
                      </TableCell>
                      <TableCell heading className="text-center w-24">
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
                        const invitation = (
                          form.formData.workspaceInvitations || []
                        ).find((inv) => inv.workspaceSlug === workspace.slug);
                        const currentRole =
                          invitation?.role || WORKSPACE_ROLE_NONE;

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
                              WORKSPACE_ROLE_NONE,
                            ].map((role) => (
                              <TableCell
                                key={workspace.slug + role}
                                className="text-center"
                              >
                                <input
                                  type="radio"
                                  name={`workspace-${workspace.slug}`}
                                  checked={currentRole === role}
                                  onChange={() =>
                                    handleRoleChange(
                                      workspace.slug,
                                      workspace.name,
                                      role,
                                    )
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
