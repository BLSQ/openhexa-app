import { ApolloClient, gql } from "@apollo/client";
import {
  LaunchNotebookServerMutation,
  LaunchNotebookServerMutationVariables,
} from "./notebooks.generated";

export async function launchNotebookServer(
  client: ApolloClient<unknown>,
  workspaceSlug: string,
) {
  const { data } = await client.mutate<
    LaunchNotebookServerMutation,
    LaunchNotebookServerMutationVariables
  >({
    mutation: gql`
      mutation launchNotebookServer($input: LaunchNotebookServerInput!) {
        launchNotebookServer(input: $input) {
          success
          server {
            name
            ready
            url
          }
        }
      }
    `,
    variables: {
      input: {
        workspaceSlug,
      },
    },
  });

  if (!data?.launchNotebookServer.success) {
    throw new Error(`Unable to launch notebook server for ${workspaceSlug}`);
  }

  return data.launchNotebookServer.server!;
}
