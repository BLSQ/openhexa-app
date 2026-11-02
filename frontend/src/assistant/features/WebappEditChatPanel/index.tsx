import { useCallback } from "react";
import EditObjectChatPanel, {
  AssistantConversation,
} from "assistant/features/EditObjectChatPanel";
import { TOOL } from "assistant/helpers/tools";
import { LinkedObjectType } from "graphql/types";

export type WebappConversation = AssistantConversation;

const SAVE_TOOLS: string[] = [
  TOOL.UpdateStaticWebapp,
  TOOL.EditStaticWebappFile,
];

type Props = {
  webappId: string;
  workspaceSlug: string;
  // The assistant committed a new version of the web app files.
  onVersionSaved?: () => void;
  conversations: WebappConversation[];
  activeConversationId: string | null;
  onConversationChange: (id: string) => void;
  onNewConversation: () => void;
  onConversationCreated: (conversation: WebappConversation) => void;
  onConversationNameChange: (id: string, name: string) => void;
  flush?: boolean;
  onClose?: () => void;
};

export default function WebappEditChatPanel({
  webappId,
  onVersionSaved,
  ...rest
}: Props) {
  const handleToolResult = useCallback(
    (toolName: string, _output: unknown, success: boolean) => {
      if (success && SAVE_TOOLS.includes(toolName)) {
        onVersionSaved?.();
      }
    },
    [onVersionSaved],
  );

  return (
    <EditObjectChatPanel
      {...rest}
      linkedObjectId={webappId}
      linkedObjectType={LinkedObjectType.StaticWebapp}
      onToolResult={handleToolResult}
    />
  );
}
