import { gql } from "@apollo/client";
import { ArrowDownTrayIcon } from "@heroicons/react/24/outline";
import { PlayIcon } from "@heroicons/react/24/solid";
import Button from "core/components/Button";
import CodeEditor, {
  CodeEditorHandle,
} from "core/components/CodeEditor/CodeEditor";
import Spinner from "core/components/Spinner";
import { useTranslation } from "next-i18next";
import { KeyboardEvent, useRef, useState } from "react";
import { buildCsv, downloadCsv } from "./csv";
import { useExecuteWorkspaceSqlLazyQuery } from "./DataStudioEditor.generated";
import DataStudioResults from "./DataStudioResults";
import DataStudioSchemaBrowser from "./DataStudioSchemaBrowser";

type DataStudioEditorProps = {
  workspaceSlug: string;
};

const MAX_ROWS_OPTIONS = [50, 100, 500, 1000, 10_000];

const DataStudioEditor = ({ workspaceSlug }: DataStudioEditorProps) => {
  const { t } = useTranslation();
  const [query, setQuery] = useState("");
  const [maxRows, setMaxRows] = useState(MAX_ROWS_OPTIONS[0]);
  const editorRef = useRef<CodeEditorHandle>(null);

  const [execute, { data, loading }] = useExecuteWorkspaceSqlLazyQuery({
    fetchPolicy: "network-only",
  });

  const result = data?.workspace?.database?.executeSQL;
  const canExport = Boolean(result?.success && (result.rows?.length ?? 0) > 0);

  const run = () => {
    if (loading || !query.trim()) {
      return;
    }
    execute({ variables: { workspaceSlug, query, maxRows } });
  };

  const exportCsv = () => {
    if (!result?.success) {
      return;
    }
    const csv = buildCsv(result.columns ?? [], result.rows ?? []);
    downloadCsv("query-results.csv", csv);
  };

  const onKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      event.preventDefault();
      run();
    }
  };

  return (
    <div className="flex gap-4">
      <DataStudioSchemaBrowser
        workspaceSlug={workspaceSlug}
        className="w-[240px] shrink-0"
        onInsert={(text) => editorRef.current?.insertText(text)}
      />
      <div className="flex min-w-0 flex-1 flex-col gap-4">
        {/* Editor block: toolbar (top) + writable editor filling the area. */}
        <div className="flex flex-col overflow-hidden rounded-md border bg-white shadow-xs">
          <div className="flex h-12 shrink-0 items-center gap-2 border-b border-gray-200 px-3">
            <Button
              onClick={run}
              disabled={loading || !query.trim()}
              leadingIcon={
                loading ? (
                  <Spinner size="xs" />
                ) : (
                  <PlayIcon className="h-4 w-4" />
                )
              }
            >
              {loading ? t("Running…") : t("Run")}
            </Button>
            <div className="ml-auto flex items-center gap-3">
              <label className="flex items-center gap-1.5 text-xs text-gray-500">
                {t("Max rows")}
                <select
                  value={maxRows}
                  onChange={(event) => setMaxRows(Number(event.target.value))}
                  className="rounded-md border border-gray-300 py-1 pr-7 pl-2 text-xs text-gray-700 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                >
                  {MAX_ROWS_OPTIONS.map((option) => (
                    <option key={option} value={option}>
                      {option.toLocaleString()}
                    </option>
                  ))}
                </select>
              </label>
              <Button
                variant="white"
                onClick={exportCsv}
                disabled={!canExport}
                leadingIcon={<ArrowDownTrayIcon className="h-4 w-4" />}
              >
                {t("Export CSV")}
              </Button>
            </div>
          </div>
          <div onKeyDown={onKeyDown} className="flex-1">
            <CodeEditor
              ref={editorRef}
              lang="sql"
              value={query}
              onChange={setQuery}
              height="45vh"
              className="!rounded-none !border-0"
            />
          </div>
        </div>

        {/* Results block: always present. */}
        <DataStudioResults loading={loading} result={result} />
      </div>
    </div>
  );
};

DataStudioEditor.queries = {
  executeSQL: gql`
    query ExecuteWorkspaceSql(
      $workspaceSlug: String!
      $query: String!
      $maxRows: Int
    ) {
      workspace(slug: $workspaceSlug) {
        slug
        database {
          executeSQL(query: $query, maxRows: $maxRows) {
            success
            errors
            errorMessage
            columns
            rows
            rowCount
            truncated
          }
        }
      }
    }
  `,
};

export default DataStudioEditor;
