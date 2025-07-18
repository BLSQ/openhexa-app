import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import Spinner from "core/components/Spinner";
import { useTranslation } from "next-i18next";
import useForm from "core/hooks/useForm";
import {
  InviteOrganizationMemberError,
  OrganizationMembershipRole,
  WorkspaceMembershipRole,
} from "graphql/types";
import SimpleSelect from "core/components/forms/SimpleSelect";
import useCacheKey from "core/hooks/useCacheKey";
import { useEffect, useState } from "react";
import { useGetWorkspacesQuery } from "core/features/SpotlightSearch/SpotlightSearch.generated";
import { useInviteOrganizationMemberMutation } from "../OrganizationMembers.generated";
import { UserPicker } from "workspaces/features/UserPicker/UserPicker";
import Input from "core/components/forms/Input";

type AddOrganizationMemberDialogProps = {
  onClose(): void;
  open: boolean;
  organizationId: string;
};

type Form = {
  user: React.ComponentProps<typeof UserPicker>["value"];
  organizationRole: OrganizationMembershipRole;
  workspaceInvitations: Array<{
    workspaceSlug: string;
    role: WorkspaceMembershipRole;
  }>;
};

type WorkspaceRoleSelection = {
  [workspaceSlug: string]: WorkspaceMembershipRole | "NONE";
};

const AddOrganizationMemberDialog = (
  props: AddOrganizationMemberDialogProps,
) => {
  const { t } = useTranslation();
  const { open, onClose, organizationId } = props;

  const [inviteOrganizationMember] = useInviteOrganizationMemberMutation({
    refetchQueries: ["OrganizationMembers"],
  });

  const { data: workspacesData, loading: workspacesLoading } =
    useGetWorkspacesQuery({
      variables: { organizationId, perPage: 100 },
      skip: !open,
    });

  const [searchTerm, setSearchTerm] = useState("");
  const [workspaceRoles, setWorkspaceRoles] = useState<WorkspaceRoleSelection>(
    {},
  );

  const clearCache = useCacheKey(["organization", organizationId]);

  // Helper function to get default workspace role based on organization role
  const getDefaultWorkspaceRole = (
    orgRole: OrganizationMembershipRole,
  ): WorkspaceMembershipRole => {
    switch (orgRole) {
      case OrganizationMembershipRole.Member:
        return WorkspaceMembershipRole.Viewer;
      case OrganizationMembershipRole.Admin:
        return WorkspaceMembershipRole.Editor;
      case OrganizationMembershipRole.Owner:
        return WorkspaceMembershipRole.Admin;
      default:
        return WorkspaceMembershipRole.Viewer;
    }
  };

  const form = useForm<Form>({
    onSubmit: async (values) => {
      // Convert workspaceRoles to workspaceInvitations format
      const workspaceInvitations = Object.entries(workspaceRoles)
        .filter(([_, role]) => role !== "NONE")
        .map(([workspaceSlug, role]) => {
          const workspace = workspacesData?.workspaces?.items?.find(
            (w) => w.slug === workspaceSlug,
          );
          return {
            workspaceSlug,
            role: role as WorkspaceMembershipRole,
            workspaceName: workspace?.name || workspaceSlug,
          };
        });

      const { data } = await inviteOrganizationMember({
        variables: {
          input: {
            userEmail: values.user!.email,
            organizationId,
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
        throw new Error("User is already a member of this organization");
      }
      if (errors.length > 0) {
        throw new Error("An error occurred while inviting the member.");
      }

      clearCache();
      handleClose();
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

  const handleClose = () => {
    onClose();
  };

  useEffect(() => {
    if (open) {
      form.resetForm();
      setSearchTerm("");
      // Initialize all workspaces to default role based on organization role
      const initialRoles: WorkspaceRoleSelection = {};
      const defaultRole = getDefaultWorkspaceRole(
        form.formData.organizationRole || OrganizationMembershipRole.Member,
      );
      workspacesData?.workspaces?.items?.forEach((workspace) => {
        initialRoles[workspace.slug] = defaultRole;
      });
      setWorkspaceRoles(initialRoles);
    }
  }, [open, form, workspacesData]);

  // Update workspace roles when organization role changes
  useEffect(() => {
    const defaultRole = getDefaultWorkspaceRole(
      form.formData.organizationRole || OrganizationMembershipRole.Member,
    );
    const updatedRoles: WorkspaceRoleSelection = {};
    workspacesData?.workspaces?.items?.forEach((workspace) => {
      updatedRoles[workspace.slug] = defaultRole;
    });
    setWorkspaceRoles(updatedRoles);
  }, [form.formData.organizationRole, workspacesData]);

  const handleRoleChange = (
    workspaceSlug: string,
    role: WorkspaceMembershipRole | "NONE",
  ) => {
    setWorkspaceRoles((prev) => ({
      ...prev,
      [workspaceSlug]: role,
    }));
  };

  const filteredWorkspaces =
    workspacesData?.workspaces?.items?.filter((workspace) =>
      workspace.name.toLowerCase().includes(searchTerm.toLowerCase()),
    ) || [];

  return (
    <Dialog open={open} onClose={handleClose} onSubmit={form.handleSubmit}>
      <Dialog.Title>{t("Invite Organization Member")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <Field name="user" label={t("User")} required>
          <UserPicker
            workspaceSlug={workspacesData?.workspaces?.items?.[0]?.slug || ""}
            value={form.formData.user!}
            onChange={(user) => form.setFieldValue("user", user)}
          />
        </Field>
        <Field name="organizationRole" label={t("Organization Role")} required>
          <SimpleSelect
            name="organizationRole"
            value={form.formData.organizationRole}
            onChange={form.handleInputChange}
            required
          >
            <option value={OrganizationMembershipRole.Member}>
              {t("Member")}
            </option>
            <option value={OrganizationMembershipRole.Admin}>
              {t("Admin")}
            </option>
            <option value={OrganizationMembershipRole.Owner}>
              {t("Owner")}
            </option>
          </SimpleSelect>
        </Field>

        <Field name="workspaces" label={t("Workspaces")} required>
          <div className="space-y-3">
            {workspacesLoading ? (
              <div className="flex items-center justify-center py-6">
                <Spinner size="xs" />
                <span className="ml-2 text-sm text-gray-500">
                  {t("Loading workspaces...")}
                </span>
              </div>
            ) : (
              <>
                {/* Search Input */}
                <div className="relative">
                  <Input
                    type="text"
                    placeholder={t("Search workspaces...")}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-8"
                  />
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg
                      className="h-4 w-4 text-gray-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                      />
                    </svg>
                  </div>
                </div>

                {/* Workspaces Grid */}
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                    <div className="grid grid-cols-6 gap-4 text-sm font-medium text-gray-700">
                      <div className="col-span-2">{t("Workspace")}</div>
                      <div className="text-center">{t("Admin")}</div>
                      <div className="text-center">{t("Editor")}</div>
                      <div className="text-center">{t("Viewer")}</div>
                      <div className="text-center">{t("None")}</div>
                    </div>
                  </div>

                  <div className="max-h-64 overflow-y-auto">
                    {filteredWorkspaces.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <p className="text-sm">
                          {searchTerm
                            ? t("No workspaces found")
                            : t("No workspaces available")}
                        </p>
                      </div>
                    ) : (
                      filteredWorkspaces.map((workspace, index) => {
                        const currentRole =
                          workspaceRoles[workspace.slug] || "NONE";

                        return (
                          <div
                            key={workspace.slug}
                            className={`grid grid-cols-6 gap-4 px-4 py-3 hover:bg-gray-50 ${
                              index !== 0 ? "border-t border-gray-100" : ""
                            } ${currentRole !== "NONE" ? "bg-blue-50" : ""}`}
                          >
                            <div className="col-span-2 flex items-center">
                              <div>
                                <div className="font-medium text-gray-900">
                                  {workspace.name}
                                </div>
                                {workspace.countries &&
                                  workspace.countries.length > 0 && (
                                    <div className="text-xs text-gray-500 mt-1">
                                      {workspace.countries
                                        .map((country) => country.code)
                                        .join(", ")}
                                    </div>
                                  )}
                              </div>
                            </div>

                            <div className="flex items-center justify-center">
                              <input
                                type="radio"
                                name={`workspace-${workspace.slug}`}
                                checked={
                                  currentRole === WorkspaceMembershipRole.Admin
                                }
                                onChange={() =>
                                  handleRoleChange(
                                    workspace.slug,
                                    WorkspaceMembershipRole.Admin,
                                  )
                                }
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                              />
                            </div>

                            <div className="flex items-center justify-center">
                              <input
                                type="radio"
                                name={`workspace-${workspace.slug}`}
                                checked={
                                  currentRole === WorkspaceMembershipRole.Editor
                                }
                                onChange={() =>
                                  handleRoleChange(
                                    workspace.slug,
                                    WorkspaceMembershipRole.Editor,
                                  )
                                }
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                              />
                            </div>

                            <div className="flex items-center justify-center">
                              <input
                                type="radio"
                                name={`workspace-${workspace.slug}`}
                                checked={
                                  currentRole === WorkspaceMembershipRole.Viewer
                                }
                                onChange={() =>
                                  handleRoleChange(
                                    workspace.slug,
                                    WorkspaceMembershipRole.Viewer,
                                  )
                                }
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                              />
                            </div>

                            <div className="flex items-center justify-center">
                              <input
                                type="radio"
                                name={`workspace-${workspace.slug}`}
                                checked={currentRole === "NONE"}
                                onChange={() =>
                                  handleRoleChange(workspace.slug, "NONE")
                                }
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                              />
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
        </Field>

        {form.submitError && (
          <div className="text-danger mt-3 text-sm">{form.submitError}</div>
        )}
      </Dialog.Content>
      <Dialog.Actions>
        <Button onClick={handleClose} variant="white">
          {t("Cancel")}
        </Button>
        <Button
          type="submit"
          className="space-x-2"
          disabled={form.isSubmitting}
        >
          {form.isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Invite Member")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default AddOrganizationMemberDialog;
