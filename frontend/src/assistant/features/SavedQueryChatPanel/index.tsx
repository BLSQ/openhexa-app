import { useCallback } from "react";
import EditObjectChatPanel, {
  AssistantConversation,
} from "assistant/features/EditObjectChatPanel";
import { InstructionSet } from "assistant/instructions";
import { TOOL } from "assistant/helpers/tools";
import { LinkedObjectType } from "graphql/types";

export type SavedQueryConversation = AssistantConversation;

type Props = {
  workspaceSlug: string;
  // The query being edited. Without one (the blank Data Studio editor) the
  // assistant only drafts SQL into the editor: there is nothing to save into yet.
  savedQueryId?: string | null;
  // A new version was saved by the assistant, with its SQL.
  onVersionSaved?: (content: string) => void;
  // The assistant drafted SQL for an editor that has no saved query yet.
  onDraftSql?: (sql: string) => void;
  conversations: SavedQueryConversation[];
  activeConversationId: string | null;
  onConversationChange: (id: string) => void;
  onNewConversation: () => void;
  onConversationCreated: (conversation: SavedQueryConversation) => void;
  onConversationNameChange: (id: string, name: string) => void;
  flush?: boolean;
  onClose?: () => void;
};

export default function SavedQueryChatPanel({
  workspaceSlug,
  savedQueryId,
  onVersionSaved,
  onDraftSql,
  ...rest
}: Props) {
  const handleToolResult = useCallback(
    (toolName: string, output: unknown, success: boolean) => {
      if (toolName !== TOOL.SaveSavedQueryVersion || !success) return;
      const content = (output as { content?: unknown })?.content;
      if (typeof content === "string") {
        onVersionSaved?.(content);
      }
    },
    [onVersionSaved],
  );

  const handleDone = useCallback(
    (output: string | null) => {
      if (!savedQueryId && output) {
        onDraftSql?.(output);
      }
    },
    [savedQueryId, onDraftSql],
  );

  return (
    <EditObjectChatPanel
      {...rest}
      workspaceSlug={workspaceSlug}
      {...(savedQueryId
        ? {
            linkedObjectId: savedQueryId,
            linkedObjectType: LinkedObjectType.SavedQuery,
          }
        : { instructionSet: InstructionSet.GENERATE_SQL })}
      onToolResult={handleToolResult}
      onDone={handleDone}
    />
  );
}
