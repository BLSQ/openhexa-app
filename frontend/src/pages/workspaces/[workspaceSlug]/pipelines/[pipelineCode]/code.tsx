import { SparklesIcon } from "@heroicons/react/24/outline";
import AssistantProposalBanner from "assistant/features/AssistantProposalBanner";
import PipelineEditChatPanel, {
  PipelineConversation,
} from "assistant/features/PipelineEditChatPanel";
import { useResolveAssistantProposalMutation } from "assistant/graphql/mutations.generated";
import Button from "core/components/Button";
import DataCard from "core/components/DataCard";
import Page from "core/components/Page";
import Spinner from "core/components/Spinner";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import useFeature from "identity/hooks/useFeature";
import useMe from "identity/hooks/useMe";
import { useTranslation } from "next-i18next";
import { useCallback, useEffect, useRef, useState } from "react";
import { PipelineFilesEditor } from "workspaces/features/FilesEditor/PipelineFilesEditor";
import { ProposedFile } from "workspaces/features/FilesEditor/FilesEditor";
import PipelineVersionPicker from "workspaces/features/PipelineVersionPicker";
import { PipelineVersionPicker_VersionFragment } from "workspaces/features/PipelineVersionPicker/PipelineVersionPicker.generated";
import {
  useGetPipelineVersionFilesLazyQuery,
  useWorkspacePipelineCodePageQuery,
  WorkspacePipelineCodePageDocument,
  WorkspacePipelineCodePageQuery,
  WorkspacePipelineCodePageQueryVariables,
} from "workspaces/graphql/queries.generated";
import PipelineLayout from "workspaces/layouts/PipelineLayout";

type Props = {
  pipelineCode: string;
  workspaceSlug: string;
};

const WorkspacePipelineCodePage: NextPageWithLayout = (props: Props) => {
  const { pipelineCode, workspaceSlug } = props;
  const { t } = useTranslation();
  const [selectedVersion, setSelectedVersion] =
    useState<PipelineVersionPicker_VersionFragment | null>(null);
  const [proposedFiles, setProposedFiles] = useState<ProposedFile[] | null>(null);
  const [proposedToolInvocationId, setProposedToolInvocationId] = useState<string | null>(null);

  const [resolveProposal] = useResolveAssistantProposalMutation();

  const handleProposedFiles = useCallback((files: ProposedFile[] | null, toolInvocationId?: string) => {
    setProposedFiles(files);
    if (toolInvocationId !== undefined) {
      setProposedToolInvocationId(toolInvocationId);
    } else if (files !== null) {
      // New SSE proposal: clear the stored ID until Apollo refetch provides it.
      setProposedToolInvocationId(null);
    }
  }, []);

  const handleDismiss = useCallback(async () => {
    setProposedFiles(null);
    const idToDismiss = proposedToolInvocationId;
    setProposedToolInvocationId(null);
    if (idToDismiss) {
      await resolveProposal({
        variables: { toolInvocationId: idToDismiss },
      });
    }
  }, [proposedToolInvocationId, resolveProposal]);

  const [isAssistantEnabled] = useFeature("assistant");
  const me = useMe();
  const aiEnabled = me?.user?.aiSettings?.enabled ?? false;
  const showAssistant = isAssistantEnabled && aiEnabled;

  const { data, loading } = useWorkspacePipelineCodePageQuery({
    variables: {
      workspaceSlug,
      pipelineCode,
    },
  });
  const [fetchPipelineVersion, { data: versionData, loading: versionLoading }] =
    useGetPipelineVersionFilesLazyQuery();

  const [chatOpen, setChatOpen] = useState(false);
  const [conversations, setConversations] = useState<PipelineConversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);

  const seededRef = useRef(false);
  useEffect(() => {
    if (seededRef.current || !data?.pipeline) return;
    seededRef.current = true;
    const convs = data.pipeline.assistantConversations;
    setConversations(convs);
    setActiveConversationId(convs[0]?.id ?? null);
    setChatOpen(convs.length > 0);
  }, [data?.pipeline?.id]);

  const handleNewConversation = useCallback(() => {
    setActiveConversationId(null);
  }, []);

  const handleConversationCreated = useCallback(
    (conversation: PipelineConversation) => {
      setConversations((prev) => [conversation, ...prev]);
      setActiveConversationId(conversation.id);
      setChatOpen(true);
    },
    [],
  );

  const handleConversationNameChange = useCallback(
    (id: string, name: string) => {
      setConversations((prev) =>
        prev.map((c) => (c.id === id ? { ...c, name } : c)),
      );
    },
    [],
  );

  if (!data?.workspace || !data?.pipeline) {
    return null;
  }
  const { workspace, pipeline } = data;

  if (!pipeline.currentVersion) {
    return null;
  }
  const onVersionChange = (version: PipelineVersionPicker_VersionFragment) => {
    if (version) {
      setSelectedVersion(version);
      fetchPipelineVersion({
        variables: {
          versionId: version.id,
        },
      }).then();
    }
  };

  const handleVersionCreated = (
    version: PipelineVersionPicker_VersionFragment,
  ) => {
    setSelectedVersion(version);
    setProposedFiles(null);
    const idToResolve = proposedToolInvocationId;
    setProposedToolInvocationId(null);
    if (idToResolve) {
      resolveProposal({
        variables: { toolInvocationId: idToResolve },
      });
    }
    fetchPipelineVersion({
      variables: {
        versionId: version.id,
      },
    }).then();
  };

  const versionToShow = versionData?.pipelineVersion ?? pipeline.currentVersion;
  const monthlyLimitExceeded = data?.me?.assistantMonthlyLimitExceeded ?? false;

  return (
    <Page title={pipeline.name ?? t("Pipeline Code")}>
      <PipelineLayout
        workspace={workspace}
        pipeline={pipeline}
        currentTab="code"
      >
        <DataCard.FormSection>
          <div className="flex items-center gap-3">
            <label className="text-md font-medium text-gray-700">
              {t("Version")}:
            </label>
            <div className="w-70">
              <PipelineVersionPicker
                required
                value={selectedVersion ?? pipeline.currentVersion}
                pipeline={pipeline}
                onChange={onVersionChange}
              />
            </div>
            {showAssistant && (
              <Button
                onClick={() => setChatOpen((o) => !o)}
                variant="secondary"
                size="md"
                leadingIcon={<SparklesIcon className="h-4 w-4" />}
                className="ml-auto"
              >
                {t("AI Assistant")}
              </Button>
            )}
          </div>
          <div className="flex gap-4 min-h-[60vh] max-h-[65vh] overflow-hidden">
            <div className="relative flex-1 min-w-0 flex flex-col">
              {proposedFiles && (
                <AssistantProposalBanner
                  label={t("Proposed version from AI assistant")}
                  onDismiss={handleDismiss}
                  className="mb-2"
                />
              )}
              <div className="relative flex-1 min-h-0">
                {(loading || versionLoading) && (
                  <div className="absolute inset-0 backdrop-blur-xs flex justify-center items-center z-10">
                    <Spinner size="md" />
                  </div>
                )}
                <PipelineFilesEditor
                  key={versionToShow.id}
                  name={versionToShow.versionName}
                  files={versionToShow.files}
                  isEditable={true}
                  proposedFiles={proposedFiles ?? undefined}
                  workspaceSlug={workspaceSlug}
                  pipelineCode={pipelineCode}
                  pipelineId={pipeline.id}
                  onVersionCreated={handleVersionCreated}
                />
              </div>
            </div>
            {chatOpen && showAssistant && (
              <div className="w-[440px] shrink-0">
                <PipelineEditChatPanel
                  pipelineId={pipeline.id}
                  workspaceSlug={workspaceSlug}
                  monthlyLimitExceeded={monthlyLimitExceeded}
                  onProposedFiles={handleProposedFiles}
                  conversations={conversations}
                  activeConversationId={activeConversationId}
                  onConversationChange={setActiveConversationId}
                  onNewConversation={handleNewConversation}
                  onConversationCreated={handleConversationCreated}
                  onConversationNameChange={handleConversationNameChange}
                />
              </div>
            )}
          </div>
        </DataCard.FormSection>
      </PipelineLayout>
    </Page>
  );
};

WorkspacePipelineCodePage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await PipelineLayout.prefetch(ctx, client);

    const { data } = await client.query<
      WorkspacePipelineCodePageQuery,
      WorkspacePipelineCodePageQueryVariables
    >({
      query: WorkspacePipelineCodePageDocument,
      variables: {
        workspaceSlug: ctx.params!.workspaceSlug as string,
        pipelineCode: ctx.params!.pipelineCode as string,
      },
    });

    if (!data.workspace || !data.pipeline) {
      return { notFound: true };
    }

    return {
      props: {
        workspaceSlug: ctx.params!.workspaceSlug,
        pipelineCode: ctx.params!.pipelineCode,
      },
    };
  },
});

export default WorkspacePipelineCodePage;
