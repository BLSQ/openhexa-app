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
import { Trans, useTranslation } from "next-i18next";
import useForm from "core/hooks/useForm";
import {
  OrganizationMembershipRole,
  WorkspaceMembershipRole,
  UpdateOrganizationMemberError,
  WorkspacePermissionInput,
} from "graphql/types";
import SimpleSelect from "core/components/forms/SimpleSelect";
import useCacheKey from "core/hooks/useCacheKey";
import React, { useEffect, useState } from "react";
import { useUpdateOrganizationMemberMutation } from "organizations/features/OrganizationMembers/OrganizationMembers.generated";
import { formatOrganizationMembershipRole } from "organizations/helpers/organization";
import SearchInput from "core/features/SearchInput";
import { gql } from "@apollo/client";
import { OrganizationMembersQuery } from "../OrganizationMembers.generated";
import { UpdateOrganizationMemberDialog_OrganizationMemberFragment } from "./UpdateOrganizationMemberDialog.generated";

type UpdateOrganizationMemberDialogProps = {
  onClose(): void;
  open: boolean;
  member: UpdateOrganizationMemberDialog_OrganizationMemberFragment;
  organization: NonNullable<OrganizationMembersQuery["organization"]>;
};

type Form = {
  organizationRole: OrganizationMembershipRole;
  workspacePermissions: WorkspacePermissionInput[];
};

const UpdateOrganizationMemberDialog = (
  props: UpdateOrganizationMemberDialogProps,
) => {
  const { t } = useTranslation();
  const { open, onClose, member, organization } = props;

  const [updateOrganizationMember] = useUpdateOrganizationMemberMutation({
    refetchQueries: ["OrganizationMembers"],
  });

  const [searchTerm, setSearchTerm] = useState("");

  const clearCache = useCacheKey(["organization", organization.id]);

  const form = useForm<Form>({
    onSubmit: async (values) => {
      const result = await updateOrganizationMember({
        variables: {
          input: {
            id: member.id,
            role: values.organizationRole,
            workspacePermissions: values.workspacePermissions,
          },
        },
      });

      if (!result.data?.updateOrganizationMember.success) {
        const errors = result.data?.updateOrganizationMember.errors || [];
        if (errors.includes(UpdateOrganizationMemberError.PermissionDenied)) {
          throw new Error(t("You are not authorized to perform this action"));
        }
        if (errors.includes(UpdateOrganizationMemberError.NotFound)) {
          throw new Error(t("Organization member not found"));
        }
        throw new Error(t("Failed to update member permissions"));
      }
      clearCache();
      onClose();
    },
    initialState: {
      organizationRole: member.role,
      workspacePermissions: organization.workspaces.items.map((workspace) => {
        const existingMembership = member.workspaceMemberships.find(
          ({ workspace: { slug } }) => slug === workspace.slug,
        );
        return {
          workspaceSlug: workspace.slug,
          role: existingMembership?.role || null,
        };
      }),
    },
  });

  useEffect(() => {
    if (open) {
      setSearchTerm("");
    }
  }, [open]);

  const handleRoleChange = (
    workspaceSlug: string,
    role: WorkspaceMembershipRole | null,
  ) => {
    const currentPermissions = form.formData.workspacePermissions || [];
    const updatedPermissions = currentPermissions.map((permission) =>
      permission.workspaceSlug === workspaceSlug
        ? { ...permission, role }
        : permission,
    );
    form.setFormData({
      ...form.formData,
      workspacePermissions: updatedPermissions,
    });
  };

  const filteredWorkspaces = organization.workspaces.items.filter((workspace) =>
    workspace.name.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <Dialog
      open={open}
      onClose={onClose}
      onSubmit={form.handleSubmit}
      maxWidth="max-w-4xl"
    >
      <Dialog.Title>{t("Update Member Permissions")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <div>
          <p className="text-sm text-gray-600 mb-4">
            <Trans>
              Updating permissions for{" "}
              <b className="font-medium">{member.user.displayName}</b>
            </Trans>
          </p>
        </div>

        <Field name="organizationRole" label={t("Organization Role")} required>
          <SimpleSelect
            id="organizationRole"
            name="organizationRole"
            value={form.formData.organizationRole}
            onChange={form.handleInputChange}
            required
            disabled={member.role === OrganizationMembershipRole.Owner}
          >
            {Object.values(OrganizationMembershipRole)
              .filter((role) => {
                if (role === OrganizationMembershipRole.Owner) {
                  return organization.permissions.manageOwners;
                }
                return true;
              })
              .map((role) => (
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
                        const permissions =
                          form.formData.workspacePermissions || [];
                        const permission = permissions.find(
                          (p) => p.workspaceSlug === workspace.slug,
                        );
                        const currentRole = permission?.role || null;

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
                              null,
                            ].map((role) => (
                              <TableCell
                                key={workspace.slug + (role || "NONE")}
                                className="text-center"
                              >
                                <input
                                  type="radio"
                                  name={`workspace-${workspace.slug}`}
                                  checked={currentRole === role}
                                  onChange={() =>
                                    handleRoleChange(workspace.slug, role)
                                  }
                                  className="h-4 w-4 text-blue-600 cursor-pointer"
                                  aria-label={`${workspace.slug} ${role || "NONE"}`}
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
          {t("Update")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

UpdateOrganizationMemberDialog.fragments = {
  organizationMember: gql`
    fragment UpdateOrganizationMemberDialog_organizationMember on OrganizationMembership {
      id
      role
      workspaceMemberships {
        id
        role
        workspace {
          slug
          name
        }
      }
      user {
        id
        displayName
        email
      }
    }
  `,
  workspace: gql`
    fragment UpdateOrganizationMemberDialog_workspace on Workspace {
      slug
      name
    }
  `,
};

export default UpdateOrganizationMemberDialog;
