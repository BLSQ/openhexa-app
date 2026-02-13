import { gql } from "@apollo/client";
import { getApolloClient } from "core/helpers/apollo";
import { FormInstance } from "core/hooks/useForm";
import { Connection, ConnectionType } from "graphql/types";
import {
  DeleteConnectionMutation,
  DeleteConnectionMutationVariables,
} from "./utils.generated";

export type FieldForm = {
  secret?: boolean;
  code: string;
  value?: string | null;
} & {
  [key: string]: any;
};

export type ConnectionForm = {
  name: string;
  description?: string;
  type: ConnectionType | null;
  [key: string]: any;
};

export type ConnectionDefinition = {
  label: string;
  color: string;
  iconSrc?: string;
  fields: FieldForm[];
  Form: React.FC<{ form: FormInstance<ConnectionForm> }>;
};

export const updateFormField = (
  form: FormInstance<ConnectionForm>,
  index: number,
  values: any,
) => {
  const newFields = [...(form.formData.fields ?? [])];
  newFields.splice(index, 1, { ...newFields[index], ...values });
  form.setFieldValue("fields", newFields);
};

export const slugify = (...keys: string[]) =>
  keys.join("_").replaceAll("-", "_").toUpperCase();

export function convertFieldsToInput(
  connectionType: ConnectionDefinition,
  fields: { [key: string]: any },
) {
  return connectionType.fields.map((f: any) => ({
    code: f.code,
    secret: Boolean(f.secret),
    value: fields[f.code],
  }));
}

export async function deleteConnection(connectionId: string) {
  const client = getApolloClient();
  const { data } = await client.mutate<
    DeleteConnectionMutation,
    DeleteConnectionMutationVariables
  >({
    mutation: gql`
      mutation DeleteConnection($input: DeleteConnectionInput!) {
        deleteConnection(input: $input) {
          success
          errors
        }
      }
    `,
    variables: { input: { id: connectionId } },
    update(cache) {
      const normalizedId = cache.identify({
        id: connectionId,
        __typename: "Connection",
      });

      cache.evict({ id: normalizedId });
      cache.gc();
    },
  });

  if (!data?.deleteConnection.success) {
    throw new Error("Impossible to delete connection");
  }
  return true;
}
