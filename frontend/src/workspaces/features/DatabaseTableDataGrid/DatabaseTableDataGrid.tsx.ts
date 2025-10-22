import { graphql } from "graphql/gql";

export const DatabaseTableDataGridWorkspaceDoc = graphql(`
  fragment DatabaseTableDataGrid_workspace on Workspace {
    slug
  }
`);

export const DatabaseTableDataGridTableDoc = graphql(`
  fragment DatabaseTableDataGrid_table on DatabaseTable {
    name
    columns {
      name
    }
  }
`);
