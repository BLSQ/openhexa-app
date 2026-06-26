import { gql } from "@apollo/client";
import { PlayIcon } from "@heroicons/react/24/solid";
import Button from "core/components/Button";
import CodeEditor from "core/components/CodeEditor/CodeEditor";
import Spinner from "core/components/Spinner";
import { useTranslation } from "next-i18next";
import { KeyboardEvent, useState } from "react";
import { useExecuteWorkspaceSqlLazyQuery } from "./DataStudioEditor.generated";
import DataStudioResults from "./DataStudioResults";

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
      <DataStudioResults loading={loading} result={result} />
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
