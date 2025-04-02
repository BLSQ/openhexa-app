import { Cog6ToothIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Link from "core/components/Link";
import Spinner from "core/components/Spinner";
import Field from "core/components/forms/Field";
import useForm from "core/hooks/useForm";
import { ConnectionType, CreateConnectionError } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useEffect, useMemo, useState } from "react";
import { useCreateConnectionMutation } from "workspaces/graphql/mutations.generated";
import Connections, {
  ConnectionForm,
  convertFieldsToInput,
} from "workspaces/helpers/connections";
import { FieldForm } from "workspaces/helpers/connections/utils";
import Help from "workspaces/layouts/WorkspaceLayout/Help";
import { CreateConnectionDialog_WorkspaceFragment } from "./CreateConnectionDialog.generated";
import { gql } from "@apollo/client";

interface CreateConnectionDialogProps {
  open: boolean;
  onClose: () => void;
  workspace: CreateConnectionDialog_WorkspaceFragment;
}

const ConnectionTypePanel = ({
  onSelect,
}: {
  onSelect(type: ConnectionType): void;
}) => {
  const { t } = useTranslation();
  return (
    <div className="space-y-4">
      <p>
        {t("You can create a connection based on our supported integrations")}
      </p>
      <div className="flex flex-wrap gap-6">
        {Object.entries(Connections)
          .filter(([key, _]) => key !== ConnectionType.Custom)
          .map(([key, connectionType], index) => (
            <button
              key={index}
              onClick={() => onSelect(key as ConnectionType)}
              className="border-1 flex h-24 w-32 flex-col items-center justify-center gap-1.5 overflow-hidden rounded-md border border-gray-100 p-2 text-center shadow-md hover:border-gray-200 hover:bg-gray-100"
            >
              {connectionType.iconSrc && (
                <img src={connectionType.iconSrc} className="h-8 w-8" alt="" />
              )}
              <div className="text-sm">{connectionType.label}</div>
            </button>
          ))}
      </div>
      <p className="pt-4">{t("Or you can create a custom connection")}</p>
      <button
        onClick={() => onSelect(ConnectionType.Custom)}
        className="border-1 flex h-24 w-32 flex-col items-center justify-center gap-1.5 overflow-hidden rounded-md border border-gray-100 p-2 text-center shadow-md hover:border-gray-200 hover:bg-gray-100"
      >
        <Cog6ToothIcon className="h-16 w-16 text-gray-500" />
        <div className="text-sm">{t("Custom")}</div>
      </button>
    </div>
  );
};

export default function CreateConnectionDialog({
  open,
  onClose,
  workspace,
}: CreateConnectionDialogProps) {
  const { t } = useTranslation();
  const [createConnection] = useCreateConnectionMutation();
  const [connectionType, setConnectionType] = useState<ConnectionType | null>(
    null,
  );
  const router = useRouter();
  const connection = useMemo(
    () => (connectionType ? Connections[connectionType] : null),
    [connectionType],
  );

  const form = useForm<ConnectionForm>({
    getInitialState() {
      return {};
    },
    validate(values) {
      const errors = {} as any;
      if (!values.name) {
        errors.name = t("Type a name for the connection");
      } else if (values.name.length > 40) {
        errors.name = t("Connection name must be shorter than 40 characters");
      }
      if (!values.description) {
        errors.name = t("Type a description");
      }

      return errors;
    },
    async onSubmit(values) {
      const { name, description, ...rest } = values;
      if (!connectionType || !connection) return;
      const { data } = await createConnection({
        variables: {
          input: {
            workspaceSlug: workspace.slug,
            name,
            type: connectionType,
            description,
            fields:
              connectionType !== ConnectionType.Custom
                ? convertFieldsToInput(connection, rest)
                : (rest.fields?.map((field: FieldForm) => ({
                    code: field.code,
                    value: field.value,
                    secret: Boolean(field.secret),
                  })) ?? []),
          },
        },
      });
      if (!data) {
        throw new Error("An unexpected error happened. Please retry later.");
      }
      const {
        success,
        errors,
        connection: newConnection,
      } = data.createConnection;
      if (success) {
        await router.push({
          pathname: "/workspaces/[workspaceSlug]/connections/[connectionId]",
          query: {
            connectionId: newConnection!.id,
            workspaceSlug: workspace.slug,
          },
        });
      } else if (
        errors.find((x) => x === CreateConnectionError.WorkspaceNotFound)
      ) {
        throw new Error(t("Unknown workspace"));
      } else if (errors.find((x) => x === CreateConnectionError.InvalidSlug)) {
        throw new Error(
          t("One of the fields is invalid. Please check your inputs."),
        );
      } else if (
        errors.find((x) => x === CreateConnectionError.PermissionDenied)
      ) {
        throw new Error(t("Permission denied"));
      }
    },
  });
  useEffect(() => {
    if (open) {
      form.resetForm();
    }
  }, [open, form]);

  useEffect(() => {
    if (open) {
      form.resetForm();
      setConnectionType(null);
    }
  }, [open, form]);

  useEffect(() => {
    form.resetForm();
    if (connection) {
      const initialValues = {} as any;
      for (const field of connection.fields) {
        initialValues[field.code] = field.defaultValue;
      }
      form.setFormData(initialValues);
    }
  }, [form, connection]);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      centered={false}
      maxWidth="max-w-4xl"
      onSubmit={connection ? form.handleSubmit : undefined}
    >
      <Dialog.Title>
        {t("Create a {{type}} connection", { type: connection?.label })}
      </Dialog.Title>
      {connection ? (
        <>
          <Dialog.Content>
            <p className="mb-5">
              You can create a connection based on our supported integrations or
              create a custom connection. Please note that connections are not
              available in already running Jupyter instances. Follow{" "}
              <Link
                href="https://github.com/BLSQ/openhexa/wiki/Using-notebooks-in-OpenHEXA#restarting-your-jupyter-server"
                target="_blank"
              >
                this guide
              </Link>{" "}
              to learn how to restart your Jupyter instance.
            </p>
            {connectionType === ConnectionType.Custom && (
              <p className="mb-5">
                The custom connection is a way to pass configuration data to the
                pipelines or the notebooks. You can add as many fields as you
                want. The fields will be available in the pipelines and the
                notebooks as environment variables and can be accessed using the
                SDK as well.
              </p>
            )}

            <div className="grid flex-1 grid-cols-2 gap-x-2 gap-y-4">
              <Field
                onChange={form.handleInputChange}
                type="text"
                name="name"
                value={form.formData.name}
                label={t("Connection name")}
                placeholder={t("Ex: My database server")}
                max={40}
                fullWidth
                help={t("Maximum 40 characters")}
                required
              />
              <Field
                onChange={form.handleInputChange}
                name="description"
                value={form.formData.description}
                className="col-span-2"
                label={t("Description")}
                fullWidth
                placeholder={t("Type a description for your connection")}
                help={t("Short description of the connection")}
                required
              />
              <connection.Form form={form} />
            </div>
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
            <Button
              type="submit"
              disabled={form.isSubmitting}
              data-testid="create-connection"
            >
              {form.isSubmitting && <Spinner size="xs" className="mr-1" />}
              {t("Create connection")}
            </Button>
          </Dialog.Actions>
        </>
      ) : (
        <>
          <Dialog.Content>
            <ConnectionTypePanel onSelect={(type) => setConnectionType(type)} />
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
          </Dialog.Actions>
        </>
      )}
    </Dialog>
  );
}

CreateConnectionDialog.fragments = {
  workspace: gql`
    fragment CreateConnectionDialog_workspace on Workspace {
      slug
    }
  `,
};
