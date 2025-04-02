import { gql } from "@apollo/client";
import { getApolloClient } from "core/helpers/apollo";
import "cronstrue/locales/en";
import "cronstrue/locales/fr";
import {
  UpdateWorkspaceTemplateMutation,
  UpdateWorkspaceTemplateMutationVariables,
} from "./templates.generated";
import { UpdateTemplateError } from "graphql/types";

export async function updateTemplate(
  templateId: string,
  values: Omit<UpdateWorkspaceTemplateMutationVariables["input"], "id">,
) {
  const client = getApolloClient();
  const { data } = await client.mutate<
    UpdateWorkspaceTemplateMutation,
    UpdateWorkspaceTemplateMutationVariables
  >({
    mutation: gql`
      mutation UpdateWorkspaceTemplate($input: UpdateTemplateInput!) {
        updatePipelineTemplate(input: $input) {
          success
          errors
          template {
            id
            name
            description
            config
          }
        }
      }
    `,
    variables: { input: { id: templateId, ...values } },
  });

  if (data?.updatePipelineTemplate.success) {
    return data.updatePipelineTemplate.template;
  } else if (
    data?.updatePipelineTemplate.errors.includes(
      UpdateTemplateError.PermissionDenied,
    )
  ) {
    throw new Error("You are not authorized to perform this action");
  }

  throw new Error("Failed to update template");
}

export async function deleteTemplateVersion(versionId: string) {
  const client = getApolloClient();
  const { data } = await client.mutate({
    mutation: gql`
      mutation DeleteTemplateVersion($input: DeleteTemplateVersionInput!) {
        deleteTemplateVersion(input: $input) {
          success
          errors
        }
      }
    `,
    variables: { input: { id: versionId } },
  });

  if (data.deleteTemplateVersion.success) {
    return true;
  }

  if (data.deleteTemplateVersion.errors.includes("PERMISSION_DENIED")) {
    throw new Error("You are not authorized to perform this action");
  }

  throw new Error("Failed to delete template version");
}
