import { useCallback } from "react";
import EditObjectChatPanel, {
  AssistantConversation,
} from "assistant/features/EditObjectChatPanel";
import { LinkedObjectType } from "graphql/types";

export type WebappConversation = AssistantConversation;
export type WebappProposedFile = { path: string; content: string };

type Props = {
  webappId: string;
  workspaceSlug: string;
  monthlyLimitExceeded: boolean;
  onProposedFiles: (
    files: WebappProposedFile[] | null,
    toolInvocationId?: string,
    deletedPaths?: string[],
  ) => void;
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
  onProposedFiles,
  ...rest
}: Props) {
  const handleProposedFiles = useCallback(
    (
      files: unknown[] | null,
      toolInvocationId?: string,
      deletedPaths?: string[],
    ) => {
      onProposedFiles(
        files as WebappProposedFile[] | null,
        toolInvocationId,
        deletedPaths,
      );
    },
    [onProposedFiles],
  );

  return (
    <EditObjectChatPanel
      {...rest}
      linkedObjectId={webappId}
      linkedObjectType={LinkedObjectType.StaticWebapp}
      proposalToolName="propose_webapp_version"
      onProposedFiles={handleProposedFiles}
    />
  );
}
