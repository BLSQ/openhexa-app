import { gql } from "@apollo/client";
import {
  LockClosedIcon,
  PencilIcon,
  PlusIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import Block, { BlockSection } from "core/components/Block";
import Button from "core/components/Button";
import DescriptionList from "core/components/DescriptionList";
import DisableClickPropagation from "core/components/DisableClickPropagation";
import { Table, TableBody, TableCell, TableRow } from "core/components/Table";
import useCacheKey from "core/hooks/useCacheKey";
import { useItemContext } from "core/hooks/useItemContext";
import useToggle from "core/hooks/useToggle";
import { ConnectionField, ConnectionType } from "graphql-types";
import { DateTime } from "luxon";
import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { useUpdateConnectionMutation } from "workspaces/graphql/mutations.generated";
import { convertFieldsToInput } from "workspaces/helpers/connection";
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
      {connection.fields.length > 0 && (
        <DescriptionList>
          {connection.fields.map((field) => (
            <DescriptionList.Item
              key={field.code}
              label={field.code}
              className="flex items-center gap-1"
            >
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
            </DescriptionList.Item>
          ))}
        </DescriptionList>
      )}
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
