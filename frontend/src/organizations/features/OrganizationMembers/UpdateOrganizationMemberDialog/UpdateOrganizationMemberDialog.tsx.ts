import { graphql } from "graphql/gql";

export const UpdateOrganizationMemberDialogOrganizationMemberDoc = graphql(`
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
`);

export const UpdateOrganizationMemberDialogWorkspaceDoc = graphql(`
fragment UpdateOrganizationMemberDialog_workspace on Workspace {
  slug
  name
}
`);
