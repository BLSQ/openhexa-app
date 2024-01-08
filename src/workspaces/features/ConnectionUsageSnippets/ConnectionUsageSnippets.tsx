import { gql } from "@apollo/client";
import CodeEditor from "core/components/CodeEditor";
import Tabs from "core/components/Tabs";
import { useMemo, useState } from "react";
import { useTranslation } from "next-i18next";
import { ConnectionUsageSnippets_ConnectionFragment } from "./ConnectionUsageSnippets.generated";
import { getUsageSnippets } from "workspaces/helpers/connections/utils";

type ConnectionUsageSnippetsProps = {
  connection: ConnectionUsageSnippets_ConnectionFragment;
};

const ConnectionUsageSnippets = (props: ConnectionUsageSnippetsProps) => {
  const { connection } = props;
  const { t } = useTranslation();

  const snippets = useMemo(() => getUsageSnippets(connection), [connection]);

  if (snippets?.length === 0) {
    return (
      <div className="text-sm text-gray-500">
        {t("There are no snippets for this type of connection.")}
      </div>
    );
  } else {
    return (
      <Tabs>
        {snippets.map((snippet) => (
          <Tabs.Tab key={snippet.lang} label={snippet.lang}>
            <CodeEditor readonly lang={snippet.lang} value={snippet.code} />
          </Tabs.Tab>
        ))}
      </Tabs>
    );
  }
};

ConnectionUsageSnippets.fragments = {
  connection: gql`
    fragment ConnectionUsageSnippets_connection on Connection {
      id
      type
      slug
      fields {
        code
      }
    }
  `,
};

export default ConnectionUsageSnippets;
