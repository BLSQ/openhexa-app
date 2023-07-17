import { gql } from "@apollo/client";
import { Cog6ToothIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import Link from "core/components/Link";
import Spinner from "core/components/Spinner";
import Title from "core/components/Title";
import useForm from "core/hooks/useForm";
import { ConnectionType, CreateConnectionError } from "graphql-types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useEffect, useMemo } from "react";
import { useCreateConnectionMutation } from "workspaces/graphql/mutations.generated";
import {
  ConnectionForm,
  CONNECTION_TYPES,
  convertFieldsToInput,
} from "workspaces/helpers/connection";
import { CreateConnectionDialog_WorkspaceFragment } from "./CreateConnectionDialog.generated";
import Help from "workspaces/layouts/WorkspaceLayout/Help";

interface CreateConnectionDialogProps {
  open: boolean;
  onClose: () => void;
  workspace: CreateConnectionDialog_WorkspaceFragment;
}

const ConnectionTypePanel = ({
  onSelect,
}: {
  onSelect(type: string): void;
}) => {
  const { t } = useTranslation();
  return (
    <div className="space-y-4">
      <p>
        {t("You can create a connection based on our supported integrations")}
      </p>
      <div className="flex flex-wrap gap-6">
        {Object.entries(CONNECTION_TYPES)
          .filter(([key, _]) => key !== ConnectionType.Custom)
          .map(([key, connectionType], index) => (
            <button
              key={index}
              onClick={() => onSelect(key)}
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
  const router = useRouter();
  const form = useForm<ConnectionForm>({
    initialState: { type: null, fields: [] },
    validate(values) {
      const errors = {} as any;

      if (!values.name) {
        errors.name = t("Type a name for the connection");
      }
      if (!values.description) {
        errors.name = t("Type a description");
      }

      return errors;
    },
    async onSubmit(values) {
      const { data } = await createConnection({
        variables: {
          input: {
            name: values.name,
            slug: values.slug,
            type: values.type!,
            workspaceSlug: workspace.slug,
            description: values.description,
            fields: convertFieldsToInput(values.fields),
          },
        },
      });
      if (!data) {
        throw new Error("An unexpected error happened. Please retry later.");
      }
      const { success, errors, connection } = data.createConnection;
      if (success) {
        await router.push({
          pathname: "/workspaces/[workspaceSlug]/connections/[connectionId]",
          query: {
            connectionId: connection!.id,
            workspaceSlug: workspace.slug,
          },
        });
        onClose();
      } else if (
        errors.find((x) => x === CreateConnectionError.WorkspaceNotFound)
      ) {
        throw new Error(t("Unknown workspace"));
      } else if (errors.find((x) => x === CreateConnectionError.InvalidSlug)) {
        throw new Error(
          t("The slug of the connection or one of the field is invalid")
        );
      } else if (
        errors.find((x) => x === CreateConnectionError.PermissionDenied)
      ) {
        throw new Error(t("Permissions denied"));
      }
    },
  });
  useEffect(() => {
    if (open) {
      form.resetForm();
    }
  }, [open, form]);

  const connectionType = useMemo(
    () => (form.formData.type ? CONNECTION_TYPES[form.formData.type] : null),
    [form.formData]
  );

  return (
    <Dialog
      open={open}
      onClose={onClose}
      centered={false}
      maxWidth={form.formData.type ? "max-w-7xl" : "max-w-3xl"}
    >
      <Dialog.Title>
        {t("Create a {{type}} connection", { type: connectionType?.label })}
      </Dialog.Title>
      {connectionType ? (
        <form onSubmit={form.handleSubmit}>
          <Dialog.Content className="flex">
            <div className="grid flex-1 grid-cols-2 gap-x-2 gap-y-4">
              <Field
                onChange={form.handleInputChange}
                type="text"
                name="name"
                value={form.formData.name}
                label={t("Connection name")}
                placeholder={t("My connection")}
                required
              />
              <Field
                onChange={form.handleInputChange}
                name="slug"
                value={form.formData.slug}
                pattern="^[a-zA-Z0-9-_]*$"
                label={t("Slug")}
                placeholder={t("MY_CONNECTION")}
              />
              <Field
                onChange={form.handleInputChange}
                name="description"
                value={form.formData.description}
                className="col-span-2"
                label={t("Description")}
                help={t("Short description of the connection")}
                required
              />
              <connectionType.Form form={form} />
              {form.submitError && (
                <p className={"my-2 text-sm text-red-600"}>
                  {form.submitError}
                </p>
              )}
            </div>
            <div className="ml-4 w-1/3 border-l-2 border-gray-100 pl-4">
              <Title level={4} className="">
                {t("Resources")}
              </Title>
              <p>Explanation of the parameters</p>
              <Link href="https://docs.openhexa.org">
                Link to the documentation
              </Link>
            </div>
          </Dialog.Content>

          <Dialog.Actions>
            <Button type="button" variant="white" onClick={onClose}>
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
        </form>
      ) : (
        <>
          <Dialog.Content>
            <ConnectionTypePanel
              onSelect={(type) => form.setFieldValue("type", type)}
            />
          </Dialog.Content>
          <Dialog.Actions>
            <div className="flex-1">
              <Help
                links={[
                  {
                    label: t("About connections"),
                    href: "https://github.com/BLSQ/openhexa/wiki/User-manual#adding-and-managing-connections",
                  },
                  {
                    label: t("Using connections"),
                    href: "https://github.com/BLSQ/openhexa/wiki/Using-notebooks-in-OpenHexa#using-connections",
                  },
                ]}
              />
            </div>
            <Button type="button" variant="white" onClick={onClose}>
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
