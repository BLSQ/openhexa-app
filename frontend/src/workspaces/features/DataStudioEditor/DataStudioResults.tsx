import Spinner from "core/components/Spinner";
import { ExecuteSqlError } from "graphql/types";
import { useTranslation } from "next-i18next";
import { ExecuteWorkspaceSqlQuery } from "./DataStudioEditor.generated";
import { stringifyCellValue } from "./format";

type ExecuteSqlResult = NonNullable<
  ExecuteWorkspaceSqlQuery["workspace"]
>["database"]["executeSQL"];

type DataStudioResultsProps = {
  loading: boolean;
  result?: ExecuteSqlResult;
};

const formatCell = (value: unknown) => {
  if (value === null || value === undefined) {
    return <span className="text-gray-300">NULL</span>;
  }
  return stringifyCellValue(value);
};

const Block = ({ children }: { children: React.ReactNode }) => (
  <div className="relative flex h-[30vh] flex-col overflow-hidden rounded-md border bg-white shadow-xs">
    {children}
  </div>
);

const DataStudioResults = ({ loading, result }: DataStudioResultsProps) => {
  const { t } = useTranslation();

  const errorLabels: Record<ExecuteSqlError, string> = {
    [ExecuteSqlError.PermissionDenied]: t(
      "You don't have permission to run queries on this database.",
    ),
    [ExecuteSqlError.QueryTimeout]: t("The query timed out."),
    [ExecuteSqlError.QueryError]: t("The query could not be executed."),
    [ExecuteSqlError.MultipleStatements]: t(
      "Only a single SQL statement can be run at a time.",
    ),
  };

  if (loading) {
    return (
      <Block>
        <div className="absolute inset-0 flex items-center justify-center">
          <Spinner size="md" />
        </div>
      </Block>
    );
  }

  if (!result) {
    return (
      <Block>
        <div className="absolute inset-0 flex items-center justify-center text-sm text-gray-400">
          {t("Results will appear here after you run a query.")}
        </div>
      </Block>
    );
  }

  if (!result.success) {
    const label =
      result.errors.map((error) => errorLabels[error] ?? error).join(" ") ||
      t("The query could not be executed.");
    return (
      <Block>
        <div className="m-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          <div className="font-medium">{label}</div>
          {result.errorMessage && (
            <pre className="mt-2 whitespace-pre-wrap font-mono text-xs text-red-600">
              {result.errorMessage}
            </pre>
          )}
        </div>
      </Block>
    );
  }

  const columns = result.columns ?? [];
  const rows = result.rows ?? [];
  const rowCount = result.rowCount ?? rows.length;

  return (
    <Block>
      {result.truncated && (
        <div className="shrink-0 border-b border-amber-200 bg-amber-50 px-3 py-1.5 text-xs text-amber-800">
          {t("Results truncated to the first {{count}} rows.", {
            count: rowCount,
          })}
        </div>
      )}
      <div className="flex-1 overflow-auto">
        <table className="w-full border-separate border-spacing-0 text-sm">
          <thead className="sticky top-0 z-10 bg-gray-50">
            <tr>
              <th className="w-10 border-b border-gray-200 px-3 py-2 text-left text-xs font-semibold text-gray-400">
                #
              </th>
              {columns.map((column) => (
                <th
                  key={column}
                  className="border-b border-gray-200 px-3 py-2 text-left font-mono text-xs font-semibold text-gray-600"
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-gray-50">
                <td className="border-b border-gray-100 px-3 py-1.5 text-right font-mono text-xs text-gray-400 select-none">
                  {rowIndex + 1}
                </td>
                {columns.map((column) => {
                  const value = row[column];
                  const isNumber = typeof value === "number";
                  return (
                    <td
                      key={column}
                      className={`border-b border-gray-100 px-3 py-1.5 text-gray-700 ${
                        isNumber ? "text-right font-mono" : ""
                      }`}
                    >
                      {formatCell(value)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex shrink-0 items-center gap-2 border-t border-gray-200 bg-gray-50/60 px-3 py-1.5 text-xs text-gray-500">
        <span className="inline-flex items-center gap-1.5">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
          {t("Query OK")}
        </span>
        <span className="font-mono">
          {t("{{count}} row", {
            count: rowCount,
            plural: "{{count}} rows",
          })}
        </span>
      </div>
    </Block>
  );
};

export default DataStudioResults;
