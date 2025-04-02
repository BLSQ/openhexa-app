import { gql } from "@apollo/client";
import Button from "core/components/Button/Button";
import Dialog from "core/components/Dialog";
import useForm from "core/hooks/useForm";
import { useEffect, useMemo } from "react";
import { useTranslation } from "next-i18next";
import Connections, {
  ConnectionForm,
  convertFieldsToInput,
  FieldForm,
} from "workspaces/helpers/connections";
import { UpdateConnectionFieldsDialog_ConnectionFragment } from "./UpdateConnectionFieldsDialog.generated";
import { ConnectionType } from "graphql/types";
import { useUpdateConnectionMutation } from "workspaces/graphql/mutations.generated";
import Help from "workspaces/layouts/WorkspaceLayout/Help";

type UpdateConnectionFieldsDialogProps = {
  open: boolean;
  connection: UpdateConnectionFieldsDialog_ConnectionFragment;
  onClose(): void;
};

const UpdateConnectionFieldsDialog = (
  props: UpdateConnectionFieldsDialogProps,
) => {
  const { open, connection, onClose } = props;
  const { t } = useTranslation();
  const definition = useMemo(() => Connections[connection.type], [connection]);
  const [updateConnection] = useUpdateConnectionMutation();
  const form = useForm<ConnectionForm>({
    getInitialState() {
      if (connection.type === ConnectionType.Custom) {
        return {
          fields: connection.fields,
        };
      } else {
        return connection.fields.reduce((acc, field) => {
          acc[field.code] = field.value;
          return acc;
        }, {} as any);
      }
    },
    async onSubmit(values) {
      await updateConnection({
        variables: {
          input: {
            id: connection.id,
            fields:
              connection.type === ConnectionType.Custom
                ? values.fields.map((field: FieldForm) => ({
                    code: field.code,
                    value: field.value,
                    secret: Boolean(field.secret),
                  }))
                : convertFieldsToInput(definition, values),
          },
        },
      });
      onClose();
    },
  });

  useEffect(() => {
    if (open) {
      form.resetForm();
    }
  }, [open, form]);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="max-w-4xl"
      onSubmit={form.handleSubmit}
    >
      <Dialog.Title onClose={onClose}>
        {t("Update connection fields for {{name}}", {
          name: connection.name,
        })}
      </Dialog.Title>
      <Dialog.Content className="grid flex-1 grid-cols-2 gap-x-2 gap-y-4 ">
        <definition.Form form={form} />

        {form.submitError && (
          <p className={"my-2 text-sm text-red-600"}>{form.submitError}</p>
        )}
      </Dialog.Content>
      <Dialog.Actions>
        <div className="flex-1">
          <Help
            links={[
              {
                label: t("About connections"),
                href: "https://github.com/BLSQ/openhexa/wiki/User-manual#adding-and-managing-connections",
              },
            ]}
          />
        </div>

        <Button variant="white" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button type="submit">{t("Save")}</Button>
      </Dialog.Actions>
    </Dialog>
  );
};

UpdateConnectionFieldsDialog.fragments = {
  connection: gql`
    fragment UpdateConnectionFieldsDialog_connection on Connection {
      id
      name
      type
      fields {
        code
        value
        secret
      }
    }
  `,
};

export default UpdateConnectionFieldsDialog;
