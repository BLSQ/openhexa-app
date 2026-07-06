import { useCallback } from "react";
import EditObjectChatPanel, {
  AssistantConversation,
} from "assistant/features/EditObjectChatPanel";
import { LinkedObjectType } from "graphql/types";
import { ProposedFile } from "workspaces/features/FilesEditor/FilesEditor";

export type PipelineConversation = AssistantConversation;

type Props = {
  pipelineId: string;
  workspaceSlug: string;
  monthlyLimitExceeded: boolean;
  onProposedFiles: (files: ProposedFile[] | null, toolInvocationId?: string) => void;
  conversations: PipelineConversation[];
  activeConversationId: string | null;
  onConversationChange: (id: string) => void;
  onNewConversation: () => void;
  onConversationCreated: (conversation: PipelineConversation) => void;
  onConversationNameChange: (id: string, name: string) => void;
};

export default function PipelineEditChatPanel({
  pipelineId,
  onProposedFiles,
  ...rest
}: Props) {
  const handleProposedFiles = useCallback(
    (files: unknown[] | null, toolInvocationId?: string) => {
      onProposedFiles(files as ProposedFile[] | null, toolInvocationId);
    },
    [onProposedFiles],
  );

  return (
    <EditObjectChatPanel
      {...rest}
      linkedObjectId={pipelineId}
      linkedObjectType={LinkedObjectType.Pipeline}
      proposalToolName="propose_pipeline_version"
      onProposedFiles={handleProposedFiles}
    />
  );
}
