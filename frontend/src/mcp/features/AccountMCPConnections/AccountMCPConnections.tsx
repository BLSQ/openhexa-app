import { ChevronDownIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Block from "core/components/Block";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Link from "core/components/Link";
import Spinner from "core/components/Spinner";
import Time from "core/components/Time";
import { CustomApolloClient } from "core/helpers/apollo";
import MCPPermissionMatrix, {
  MCPGrant,
  MCPTool,
  MCPWorkspace,
} from "mcp/features/MCPPermissionMatrix";
import {
  useRevokeMcpConnectionMutation,
  useUpdateMcpConnectionMutation,
} from "mcp/graphql/mutations.generated";
import {
  AccountMcpConnectionsDocument,
  AccountMcpConnectionsQuery,
  useAccountMcpConnectionsQuery,
} from "mcp/graphql/queries.generated";
import { Trans, useTranslation } from "next-i18next";
import { useState } from "react";

const WORKSPACES_PAGE_SIZE = 100;

type Connection = AccountMcpConnectionsQuery["mcpConnections"][number];

function grantOf(connection: Connection): MCPGrant {
  return {
    workspaceSlugs: connection.workspaces.map((workspace) => workspace.slug),
    tools: [...connection.tools],
  };
}

function canonicalGrant(grant: MCPGrant) {
  return JSON.stringify({
    workspaceSlugs: [...grant.workspaceSlugs].sort(),
    tools: [...grant.tools].sort(),
  });
}

function isSameGrant(a: MCPGrant, b: MCPGrant) {
  return canonicalGrant(a) === canonicalGrant(b);
}

function grantsNothing(grant: MCPGrant) {
  return grant.tools.length === 0;
}

const ConnectionCard = ({
  connection,
  workspaces,
  tools,
}: {
  connection: Connection;
  workspaces: MCPWorkspace[];
  tools: MCPTool[];
}) => {
  const { t } = useTranslation();
  const [draft, setDraft] = useState<MCPGrant>(() => grantOf(connection));
  const [isOpen, setOpen] = useState(false);
  const [isSaving, setSaving] = useState(false);
  const [isRevoking, setRevoking] = useState(false);
  const [updateConnection] = useUpdateMcpConnectionMutation();
  const [revokeConnection] = useRevokeMcpConnectionMutation();

  const isDirty = !isSameGrant(draft, grantOf(connection));
  const grantable = tools.filter((tool) => tool.resource).length;

  const summary = [
    draft.tools.length === grantable
      ? t("All tools")
      : t("{{count}} of {{total}} tools", {
          count: draft.tools.length,
          total: grantable,
        }),
    t("{{count}} workspaces", { count: draft.workspaceSlugs.length }),
  ].join(" · ");

  const onSave = async () => {
    setSaving(true);
    const { data } = await updateConnection({
      variables: {
        input: {
          id: connection.id,
          workspaceSlugs: draft.workspaceSlugs,
          tools: draft.tools,
        },
      },
    });
    const updated = data?.updateMCPConnection.mcpConnection;
    if (updated) {
      setDraft(grantOf(updated));
    }
    setSaving(false);
  };

  const onRevoke = async () => {
    await revokeConnection({
      variables: { input: { id: connection.id } },
      refetchQueries: [AccountMcpConnectionsDocument],
    });
    setRevoking(false);
  };

  return (
    <div className="rounded-lg border border-gray-200">
      <button
        type="button"
        aria-expanded={isOpen}
        onClick={() => setOpen(!isOpen)}
        className="flex w-full items-center gap-3 p-4 text-left hover:bg-gray-50"
      >
        <ChevronDownIcon
          className={clsx(
            "h-4 w-4 shrink-0 text-gray-400 transition-transform",
            !isOpen && "-rotate-90",
          )}
        />
        <div className="min-w-0 flex-1">
          <div className="flex items-baseline gap-2">
            <span className="font-medium text-gray-900">{connection.name}</span>
            {isDirty && (
              <span className="rounded-sm bg-amber-50 px-1.5 py-0.5 text-[11px] font-medium text-amber-700">
                {t("Unsaved")}
              </span>
            )}
          </div>
          <p
            className={clsx(
              "mt-0.5 text-sm",
              grantsNothing(draft) ? "text-amber-600" : "text-gray-500",
            )}
          >
            {grantsNothing(draft) ? t("No access granted") : summary}
          </p>
        </div>
        <span className="shrink-0 text-sm text-gray-400">
          {connection.lastUsedAt ? (
            <Trans>
              Last used <Time datetime={connection.lastUsedAt} relative />
            </Trans>
          ) : (
            t("Never used")
          )}
        </span>
      </button>

      {isOpen && (
        <div className="space-y-5 border-t border-gray-100 p-4">
          <MCPPermissionMatrix
            idPrefix={`mcp-${connection.id}`}
            grant={draft}
            workspaces={workspaces}
            tools={tools}
            onChange={setDraft}
            disabled={isSaving}
          />
          <div className="flex items-center justify-end gap-4 border-t border-gray-100 pt-4">
            <div className="flex gap-2">
              <Button variant="danger" onClick={() => setRevoking(true)}>
                {t("Revoke")}
              </Button>
              <Button disabled={!isDirty || isSaving} onClick={onSave}>
                {isSaving && <Spinner size="xs" className="mr-1" />}
                {t("Save")}
              </Button>
            </div>
          </div>
        </div>
      )}

      <Dialog open={isRevoking} onClose={() => setRevoking(false)}>
        <Dialog.Title>{t("Revoke connection")}</Dialog.Title>
        <Dialog.Content className="space-y-4">
          <p>
            <Trans>
              <b>{connection.name}</b> will lose access immediately and has to
              be authorized again to reconnect.
            </Trans>
          </p>
        </Dialog.Content>
        <Dialog.Actions>
          <Button variant="white" onClick={() => setRevoking(false)}>
            {t("Cancel")}
          </Button>
          <Button variant="danger" onClick={onRevoke}>
            {t("Revoke")}
          </Button>
        </Dialog.Actions>
      </Dialog>
    </div>
  );
};

const AccountMCPConnections = () => {
  const { t } = useTranslation();
  const { data } = useAccountMcpConnectionsQuery({
    variables: { page: 1, perPage: WORKSPACES_PAGE_SIZE },
  });

  const connections = data?.mcpConnections ?? [];

  return (
    <Block id="mcp-connections">
      <Block.Header>{t("MCP connections")}</Block.Header>
      <Block.Content>
        {connections.length === 0 ? (
          <div className="space-y-2 py-2">
            <p className="text-sm text-gray-700">
              {t("No AI assistant is connected to your account yet.")}
            </p>
            <p className="text-sm text-gray-500">
              {t(
                "Once you connect one, you can choose the tools and workspaces it may use, and change that at any time.",
              )}
            </p>
            <Link href="/mcp/wiki" className="text-sm">
              {t("Connect an assistant")}
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {connections.map((connection) => (
              <ConnectionCard
                key={connection.id}
                connection={connection}
                workspaces={data?.workspaces.items ?? []}
                tools={data?.mcpTools ?? []}
              />
            ))}
          </div>
        )}
      </Block.Content>
    </Block>
  );
};

AccountMCPConnections.prefetch = async (client: CustomApolloClient) =>
  client.query({
    query: AccountMcpConnectionsDocument,
    variables: { page: 1, perPage: WORKSPACES_PAGE_SIZE },
  });

export default AccountMCPConnections;
