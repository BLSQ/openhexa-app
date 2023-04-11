import { gql } from "@apollo/client";
import {
  LockClosedIcon,
  PencilIcon,
  PlusIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import { BlockSection } from "core/components/Block";
import Button from "core/components/Button";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import useCacheKey from "core/hooks/useCacheKey";
import { ConnectionField, ConnectionType } from "graphql-types";
import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { useUpdateConnectionMutation } from "workspaces/graphql/mutations.generated";
import { convertFieldsToInput, slugify } from "workspaces/helpers/connection";
import ConnectionFieldDialog from "../ConnectionFieldDialog";
import { ConnectionFieldsSection_ConnectionFragment } from "./ConnectionFieldsSection.generated";

type ConnectionFieldsSectionProps = {
  connection: ConnectionFieldsSection_ConnectionFragment;
};

const ConnectionFieldsSection = (props: ConnectionFieldsSectionProps) => {
  const { connection } = props;
  const { t } = useTranslation();
  const [editedState, setEditedState] = useState<{
    field?: React.ComponentProps<typeof ConnectionFieldDialog>["field"];
    isOpen: boolean;
  }>({
    isOpen: false,
  });
  const [updateConnection] = useUpdateConnectionMutation();
  const clearCache = useCacheKey(["connections", connection.id]);

  const onFieldSave: React.ComponentProps<
    typeof ConnectionFieldDialog
  >["onSave"] = async (field) => {
    const fields = [...connection.fields];
    const idx = fields.findIndex((x) => x.code === field.code);
    if (idx !== -1) {
      fields[idx] = field;
    } else {
      fields.push(field as ConnectionField);
    }

    await updateConnection({
      variables: {
        input: {
          id: connection.id,
          fields: convertFieldsToInput(fields),
        },
      },
    });
    clearCache();
  };

  const onFieldDelete = async (field: Pick<ConnectionField, "code">) => {
    if (
      window.confirm(
        t("Are you sure to delete this field from the connection?")
      )
    ) {
      await updateConnection({
        variables: {
          input: {
            id: connection.id,
            fields: convertFieldsToInput(
              connection.fields.filter((f) => f.code !== field.code)
            ),
          },
        },
      });
      clearCache();
    }
  };

  return (
    <BlockSection
      collapsible={false}
      title={(open) => (
        <div className="flex flex-1 items-center justify-between">
          <h4 className="font-medium">{t("Fields")}</h4>

          {connection.type === ConnectionType.Custom &&
            connection.permissions.update && (
              <Button
                size="sm"
                variant="white"
                leadingIcon={<PlusIcon className="h-4 w-4" />}
                onClick={() => setEditedState({ isOpen: true })}
              >
                {t("Add field")}
              </Button>
            )}
        </div>
      )}
    >
      {connection.fields.length === 0 && (
        <span className="text-sm text-gray-500">
          {t("There are no fields for this connection yet.")}
        </span>
      )}
      <DataGrid
        className="max-2w-lg w-3/4 rounded-md border"
        data={connection.fields}
        fixedLayout={true}
        defaultPageSize={5}
      >
        <TextColumn className="py-3" label={t("Name")} accessor={"code"} />
        <BaseColumn label={t("Environment variable")} accessor={"code"}>
          {(value) => (
            <code className="rounded-md bg-slate-100 p-1.5 font-mono text-xs font-medium text-gray-600">
              {slugify(connection.slug, value)}
            </code>
          )}
        </BaseColumn>
        <BaseColumn
          className="flex justify-start gap-x-2 text-gray-900"
          label={t("Value")}
        >
          {(field) => (
            <>
              {field.secret && <LockClosedIcon className="h-3 w-3" />}
              {field.secret && "*********"}
              {!field.secret &&
                (field.value || (
                  <span className="text-sm italic text-gray-500">
                    {t("No value")}
                  </span>
                ))}
              <button
                onClick={() => setEditedState({ isOpen: true, field })}
                className="ml-2 rounded-sm text-blue-500  hover:text-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2"
                title={t("Update")}
              >
                <PencilIcon className="h-3.5 w-3.5" />
              </button>
              {connection.type === ConnectionType.Custom && (
                <button
                  title={t("Delete")}
                  className=" rounded p-0.5 text-red-500 hover:bg-red-500 hover:text-white focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                  onClick={() => onFieldDelete(field)}
                >
                  <TrashIcon className="h-3.5 w-3.5" />
                </button>
              )}
            </>
          )}
        </BaseColumn>
      </DataGrid>
      <ConnectionFieldDialog
        onSave={onFieldSave}
        onClose={() => setEditedState({ isOpen: false })}
        open={editedState.isOpen}
        field={editedState.field}
      />
    </BlockSection>
  );
};

ConnectionFieldsSection.fragments = {
  connection: gql`
    fragment ConnectionFieldsSection_connection on Connection {
      id
      type
      slug
      fields {
        code
        value
        secret
      }
      permissions {
        update
      }
    }
  `,
};

export default ConnectionFieldsSection;
