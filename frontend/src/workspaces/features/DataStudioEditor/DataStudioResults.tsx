import { ApolloError } from "@apollo/client";
import Button from "core/components/Button";
import Spinner from "core/components/Spinner";
import {
  classifyTransportError,
  TransportErrorKind,
} from "core/helpers/errors";
import { ExecuteSqlError } from "graphql/types";
import { useTranslation } from "next-i18next";
import { memo } from "react";
import { ExecuteWorkspaceSqlQuery } from "./DataStudioEditor.generated";
import ResultsTable from "./ResultsTable";

type ExecuteSqlResult = NonNullable<
  ExecuteWorkspaceSqlQuery["workspace"]
>["database"]["executeSQL"];

type DataStudioResultsProps = {
  loading: boolean;
  result?: ExecuteSqlResult;
  // Transport-level failure (network down, 5xx, request too large, GraphQL
  // error) as opposed to a query that ran but reported success: false.
  error?: ApolloError;
  onRetry?: () => void;
};

// The grid is a preview: rendering tens of thousands of rows as live DOM is slow,
// and users scan rather than scroll the full set. The complete result stays
// available through CSV export.
const MAX_DISPLAYED_ROWS = 500;

// EXPLAIN returns a single column with this exact name, one plan line per row.
const QUERY_PLAN_COLUMN = "QUERY PLAN";

const Block = ({ children }: { children: React.ReactNode }) => (
  <div className="relative flex h-full flex-col overflow-hidden bg-white">
    {children}
  </div>
);

const DataStudioResults = ({
  loading,
  result,
  error,
  onRetry,
}: DataStudioResultsProps) => {
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

  const transportErrorLabels: Record<TransportErrorKind, string> = {
    "too-large": t(
      "The query or its result is too large. Try lowering the maximum number of rows or narrowing your query.",
    ),
    connection: t(
      "Couldn't reach the server. Check your connection and try again.",
    ),
    server: t(
      "Something went wrong while running your query. Please try again.",
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

  if (error) {
    return (
      <Block>
        <div className="m-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          <div className="font-medium">
            {transportErrorLabels[classifyTransportError(error)]}
          </div>
          <details className="mt-2">
            <summary className="cursor-pointer text-xs text-red-600 select-none">
              {t("Technical details")}
            </summary>
            <pre className="mt-1 whitespace-pre-wrap font-mono text-xs text-red-600">
              {error.message}
            </pre>
          </details>
          {onRetry && (
            <Button
              variant="danger"
              size="sm"
              onClick={onRetry}
              className="mt-3"
            >
              {t("Retry")}
            </Button>
          )}
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

  // An EXPLAIN plan conveys its tree structure through leading whitespace, so
  // its single column is rendered monospace and whitespace-preserving to keep
  // the tree aligned (like DBeaver). Unlike a data set, a plan is bounded and
  // read as a whole, so it is never row-capped.
  const isQueryPlan = columns.length === 1 && columns[0] === QUERY_PLAN_COLUMN;
  const displayedRows = isQueryPlan ? rows : rows.slice(0, MAX_DISPLAYED_ROWS);
  const hasHiddenRows = rows.length > displayedRows.length;

  return (
    <Block>
      {result.truncated && (
        <div className="shrink-0 border-b border-amber-200 bg-amber-50 px-3 py-1.5 text-xs text-amber-800">
          {t("Results truncated to the first {{count}} rows.", {
            count: rowCount,
          })}
        </div>
      )}
      <ResultsTable
        columns={columns}
        rows={displayedRows}
        columnClassName={
          isQueryPlan
            ? { [QUERY_PLAN_COLUMN]: "whitespace-pre font-mono" }
            : undefined
        }
      />
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
          {typeof result.durationMs === "number" &&
            ` · ${result.durationMs.toLocaleString()} ms`}
        </span>
        {hasHiddenRows && (
          <span className="ml-auto text-gray-400">
            {t(
              "Showing the first {{count}} rows — export for the full result.",
              {
                count: displayedRows.length,
              },
            )}
          </span>
        )}
      </div>
    </Block>
  );
};

// Memoised because the SQL text lives in DataStudioEditor's state: without this,
// every keystroke re-renders the grid, reconciling up to MAX_DISPLAYED_ROWS rows
// worth of cells for an input this component does not even read. Apollo keeps
// `data` referentially stable between renders and `onRetry` is memoised in
// useDataStudioQuery, so the props only change when a query actually resolves.
export default memo(DataStudioResults);
