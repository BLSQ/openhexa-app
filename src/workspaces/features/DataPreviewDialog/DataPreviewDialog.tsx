import { gql, useQuery } from "@apollo/client";
import Button from "core/components/Button";
import DataGrid from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Dialog from "core/components/Dialog";
import { TableColumn } from "graphql-types";
import { useTranslation } from "next-i18next";
import { WorkspaceDatabaseTableDataQuery } from "./DataPreviewDialog.generated";

const DataPreviewDialog = ({
  open,
  workspaceSlug,
  tableName,
  onClose,
}: {
  open: boolean;
  workspaceSlug: string;
  tableName: string;
  onClose: () => void;
}) => {
  const { t } = useTranslation();
  const { data } = useQuery<WorkspaceDatabaseTableDataQuery>(
    gql`
      query WorkspaceDatabaseTableData(
        $workspaceSlug: String!
        $tableName: String!
      ) {
        workspace(slug: $workspaceSlug) {
          slug
          database {
            table(name: $tableName) {
              columns {
                name
                type
              }
              sample
            }
          }
        }
      }
    `,
    { variables: { workspaceSlug: workspaceSlug, tableName: tableName } }
  );

  if (!data?.workspace?.database.table) {
    return null;
  }
  const { workspace } = data;
  const { table } = workspace.database;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="max-w-6xl" centered={false}>
      <Dialog.Title>
        {t("Sample data for {{name}}", { name: tableName })}
      </Dialog.Title>
      <Dialog.Content>
        <div>
          <p className="text-gray-600">
            {t(
              "The following table gives you a preview of data available in {{name}}",
              { name: tableName }
            )}
          </p>
          <DataGrid
            data={table?.sample}
            fixedLayout={false}
            className="mt-4"
            defaultPageSize={5}
          >
            {table?.columns.map((c, index) => (
              <TextColumn
                key={index}
                className="py-3 font-medium"
                name={c.name}
                label={c.name}
                accessor={(row) => row[c.name]}
                defaultValue="-"
              />
            ))}
          </DataGrid>
        </div>
      </Dialog.Content>
      <Dialog.Actions>
        <Button onClick={onClose}>{t("Close")}</Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default DataPreviewDialog;
