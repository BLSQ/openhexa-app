import { gql } from "@apollo/client";
import { LockClosedIcon, PencilIcon } from "@heroicons/react/24/outline";
import { BlockSection } from "core/components/Block";
import Clipboard from "core/components/Clipboard";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import { useState } from "react";
import { useTranslation } from "next-i18next";
import { slugify } from "workspaces/helpers/connections/utils";
import UpdateConnectionFieldsDialog from "../UpdateConnectionFieldsDialog/UpdateConnectionFieldsDialog";
import { ConnectionFieldsSection_ConnectionFragment } from "./ConnectionFieldsSection.generated";

type ConnectionFieldsSectionProps = {
  connection: ConnectionFieldsSection_ConnectionFragment;
};

const ConnectionFieldsSection = (props: ConnectionFieldsSectionProps) => {
  const { connection } = props;
  const { t } = useTranslation();
  const [showUpdateDialog, setShowUpdateDialog] = useState(false);

  return (
    <BlockSection
      collapsible={false}
      title={(open) => (
        <div className="flex flex-1 items-center">
          <h4 className="font-medium">{t("Fields")}</h4>

          {connection.permissions.update && (
            <button
              className="ml-4 inline-flex items-center gap-1 text-sm text-blue-500 hover:text-blue-400"
              onClick={() => setShowUpdateDialog(true)}
            >
              {t("Edit")}
              <PencilIcon className="h-4" />
            </button>
          )}
        </div>
      )}
    >
      {connection.fields.length === 0 ? (
        <span className="text-sm text-gray-500">
          {t("There are no fields for this connection yet.")}
        </span>
      ) : (
        <DataGrid
          className="rounded-md border 2xl:w-2/4"
          data={connection.fields}
          fixedLayout={false}
        >
          <TextColumn
            className="py-3 font-mono"
            label={t("Name")}
            accessor={"code"}
          />

          <BaseColumn
            className="flex justify-start gap-x-2 font-mono text-gray-900"
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
                {!field.secret && field.value && (
                  <Clipboard value={field.value} />
                )}
              </>
            )}
          </BaseColumn>
        </DataGrid>
      )}
      <UpdateConnectionFieldsDialog
        open={showUpdateDialog}
        onClose={() => setShowUpdateDialog(false)}
        connection={connection}
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
      ...UpdateConnectionFieldsDialog_connection
    }
    ${UpdateConnectionFieldsDialog.fragments.connection}
  `,
};

export default ConnectionFieldsSection;
