import { graphql } from "graphql/gql";

export const OrganizationOrganizationDoc = graphql(`
fragment Organization_organization on Organization {
  id
  name
  shortName
  workspaces {
    totalItems
    items {
      slug
      name
      countries {
        code
      }
    }
  }
  permissions {
    createWorkspace
    archiveWorkspace
    manageMembers
    manageOwners
  }
  members {
    totalItems
  }
}
`);

export const OrganizationDatasetLinkDoc = graphql(`
fragment OrganizationDataset_link on DatasetLink {
  id
  workspace {
    slug
    name
  }
  dataset {
    id
    slug
    name
    description
    updatedAt
    sharedWithOrganization
    workspace {
      slug
      name
    }
    links(page: 1, perPage: 50) {
      items {
        workspace {
          slug
          name
        }
      }
    }
  }
}
`);

export const OrganizationWorkspaceWorkspaceDoc = graphql(`
fragment OrganizationWorkspace_workspace on Workspace {
  slug
  name
  createdAt
  updatedAt
  countries {
    code
  }
  createdBy {
    ...UserAvatar_user
  }
  members {
    totalItems
  }
  permissions {
    manageMembers
    delete
  }
}
`);
