import { graphql } from "graphql/gql";

export const FilesEditorFileDoc = graphql(`
fragment FilesEditor_file on FileNode {
  id
  name
  path
  type
  content
  parentId
  autoSelect
  language
  lineCount
}
`);
