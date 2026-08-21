import { ApolloError } from "@apollo/client";
import clsx from "clsx";
import Button from "core/components/Button";
import Spinner from "core/components/Spinner";
import {
  classifyTransportError,
  TransportErrorKind,
} from "core/helpers/errors";
import { ExecuteSqlError } from "graphql/types";
import dynamic from "next/dynamic";
import { useTranslation } from "next-i18next";
import { memo, useState } from "react";
import { detectChart } from "./chart";
import { ExecuteWorkspaceSqlQuery } from "./DataStudioEditor.generated";
import { detectMap, toFeatures } from "./map";
import ResultsChart from "./ResultsChart";
import ResultsTable from "./ResultsTable";
import WidgetHint from "./WidgetHint";

// MapLibre reads `window` while its module initialises, which a server render
// cannot provide, and the whole mapping stack is dead weight for the queries
// that return no geography — the common case. It is also an order of magnitude
// heavier than the chart library, so loading it only when a map is actually
// shown keeps it out of the editor's bundle, which charts (bundled normally) do
// not need to pay for.
const ResultsMap = dynamic(() => import("./ResultsMap"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full items-center justify-center">
      <Spinner size="md" />
    </div>
  ),
});

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

// A local tab strip rather than core/components/Tabs: the results panel fills a
// flex column and the table has to keep its own scroll area, which the shared
// component's panels do not size for, and its page-level chrome is heavier than
// this dense toolbar.
const TabButton = ({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) => (
  <button
    type="button"
    role="tab"
    aria-selected={active}
    onClick={onClick}
    className={clsx(
      "border-b-2 px-1 py-1.5 text-xs font-medium transition-colors",
      active
        ? "border-blue-600 text-gray-900"
        : "border-transparent text-gray-500 hover:text-gray-700",
    )}
  >
    {children}
  </button>
);

const DataStudioResults = ({
  loading,
  result,
  error,
  onRetry,
}: DataStudioResultsProps) => {
  const { t } = useTranslation();
  const [tab, setTab] = useState<"widget" | "table">("widget");

  const errorLabels: Record<ExecuteSqlError, string> = {
    [ExecuteSqlError.PermissionDenied]: t(
      "You don't have permission to run queries on this database.",
    ),
    [ExecuteSqlError.QueryTimeout]: t("The query timed out."),
    [ExecuteSqlError.QueryError]: t("The query could not be executed."),
    [ExecuteSqlError.MultipleStatements]: t(
      "Only a single SQL statement can be run at a time.",
    ),
    // executeSavedQuery shares this enum and is the only field that can return
    // this value; the editor submits SQL directly, so it never renders here.
    [ExecuteSqlError.SavedQueryNotFound]: t("The saved query was not found."),
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

  // Column names decide the presentation: when they follow a widget convention
  // the query is a little dashboard rather than a result set. Charts are looked
  // for first, so a result that somehow satisfies both stays predictable.
  const chart = isQueryPlan ? null : detectChart(columns, rows);
  const mapSource = isQueryPlan || chart ? null : detectMap(columns, rows);
  const hasWidget = chart !== null || mapSource !== null;
  const showWidget = hasWidget && tab === "widget";
  const mapFeatures = mapSource ? toFeatures(mapSource, rows) : null;

  return (
    <Block>
      {result.truncated && (
        <div className="shrink-0 border-b border-amber-200 bg-amber-50 px-3 py-1.5 text-xs text-amber-800">
          {t("Results truncated to the first {{count}} rows.", {
            count: rowCount,
          })}
        </div>
      )}
      {hasWidget && (
        <div
          role="tablist"
          className="flex shrink-0 items-center gap-4 border-b border-gray-200 px-3"
        >
          <TabButton active={tab === "widget"} onClick={() => setTab("widget")}>
            {chart ? t("Chart") : t("Map")}
          </TabButton>
          <TabButton active={tab === "table"} onClick={() => setTab("table")}>
            {t("Table")}
          </TabButton>
        </div>
      )}
      {showWidget ? (
        <div className="min-h-0 flex-1">
          {/* Both widgets read every returned row: the 500-row cap below exists
              to keep the DOM small, which an aggregated chart does not suffer
              from and which markers on a canvas suffer from far less. */}
          {chart ? (
            <ResultsChart kind={chart} rows={rows} />
          ) : mapSource!.kind === "unreadable-geometry" ? (
            // Asked for as a map but still in PostGIS' binary form. Saying so —
            // with the one-line fix — beats a blank map or silently dropping
            // back to the table, which would look like the feature is broken.
            <div className="flex h-full flex-col items-center justify-center gap-2 px-6 text-center text-sm text-gray-500">
              <p>
                {t(
                  'The "{{column}}" column holds binary geometry, which cannot be drawn directly.',
                  { column: mapSource!.column },
                )}
              </p>
              <p className="text-gray-400">
                {t("Select it as GeoJSON to map it:")}{" "}
                <code className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs text-gray-700">
                  ST_AsGeoJSON({mapSource!.column}) AS {mapSource!.column}
                </code>
              </p>
            </div>
          ) : (
            <ResultsMap features={mapFeatures?.features ?? []} />
          )}
        </div>
      ) : (
        <ResultsTable
          columns={columns}
          rows={displayedRows}
          columnClassName={
            isQueryPlan
              ? { [QUERY_PLAN_COLUMN]: "whitespace-pre font-mono" }
              : undefined
          }
        />
      )}
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
        {/* Only offered when the result was not charted: that is exactly the
            user who has not met the convention yet. Once a chart is drawn the
            tab strip above already advertises the feature, and an invitation
            to chart what is already a chart would read as a mistake. A query
            plan is never chartable, so it is excluded too.

            Kept in this left cluster rather than pushed to the right: the
            workspace layout pins its floating help button to the viewport's
            bottom-right corner, which overlaps the end of this bar and would
            bury the hint under it. */}
        {!hasWidget && !isQueryPlan && <WidgetHint />}
        {/* Each view reports only the cap that applies to what is on screen:
            the row cap belongs to the table, the feature cap to the map. */}
        {showWidget
          ? !!mapFeatures?.hidden && (
              <span className="ml-auto text-gray-400">
                {t("Showing the first {{count}} locations.", {
                  count: mapFeatures.features.length,
                })}
              </span>
            )
          : hasHiddenRows && (
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
