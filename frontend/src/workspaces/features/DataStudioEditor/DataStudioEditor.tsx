import { gql } from "@apollo/client";
import { PlayIcon } from "@heroicons/react/24/solid";
import Button from "core/components/Button";
import CodeEditor from "core/components/CodeEditor/CodeEditor";
import Spinner from "core/components/Spinner";
import { useTranslation } from "next-i18next";
import { KeyboardEvent, useState } from "react";
import { useExecuteWorkspaceSqlLazyQuery } from "./DataStudioEditor.generated";

type DataStudioEditorProps = {
  workspaceSlug: string;
};

const DataStudioEditor = ({ workspaceSlug }: DataStudioEditorProps) => {
  const { t } = useTranslation();
  const [query, setQuery] = useState("");

  const [execute, { data, loading }] = useExecuteWorkspaceSqlLazyQuery({
    fetchPolicy: "network-only",
  });

  const result = data?.workspace?.database?.executeSQL;

  const run = () => {
    if (loading || !query.trim()) {
      return;
    }
    execute({ variables: { workspaceSlug, query } });
  };

  const onKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      event.preventDefault();
      run();
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Editor block: toolbar (top) + writable editor filling the area. */}
      <div className="flex flex-col overflow-hidden rounded-md border bg-white shadow-xs">
        <div className="flex h-12 shrink-0 items-center gap-2 border-b border-gray-200 px-3">
          <Button
            onClick={run}
            disabled={loading || !query.trim()}
            leadingIcon={
              loading ? <Spinner size="xs" /> : <PlayIcon className="h-4 w-4" />
            }
          >
            {loading ? t("Running…") : t("Run")}
          </Button>
          {/* Room for future actions (Save, Export CSV, …). */}
          <div className="ml-auto" />
        </div>
        <div onKeyDown={onKeyDown} className="flex-1">
          <CodeEditor
            lang="sql"
            value={query}
            onChange={setQuery}
            height="45vh"
            className="!rounded-none !border-0"
          />
        </div>
      </div>

      {/* Results block: always present. */}
      <div className="relative min-h-[30vh] overflow-auto rounded-md border bg-white shadow-xs">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <Spinner size="md" />
          </div>
        ) : !result ? (
          <div className="absolute inset-0 flex items-center justify-center text-sm text-gray-400">
            {t("Results will appear here after you run a query.")}
          </div>
        ) : !result.success ? (
          <div className="m-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {result.errorMessage || result.errors.join(", ")}
          </div>
        ) : (
          <pre className="p-3 text-xs">
            {JSON.stringify(
              { columns: result.columns, rows: result.rows },
              null,
              2,
            )}
          </pre>
        )}
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
