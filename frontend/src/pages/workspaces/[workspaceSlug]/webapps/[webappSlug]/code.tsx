import { SparklesIcon } from "@heroicons/react/24/outline";
import AssistantProposalBanner from "assistant/features/AssistantProposalBanner";
import WebappEditChatPanel, {
  WebappConversation,
  WebappProposedFile,
} from "assistant/features/WebappEditChatPanel";
import { useResolveAssistantProposalMutation } from "assistant/graphql/mutations.generated";
import Button from "core/components/Button";
import DataCard from "core/components/DataCard";
import Page from "core/components/Page";
import Spinner from "core/components/Spinner";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import useFeature from "identity/hooks/useFeature";
import useMe from "identity/hooks/useMe";
import { WebappType } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "react-toastify";
import {
  useWorkspaceWebappPageQuery,
  WorkspaceWebappPageDocument,
  WorkspaceWebappPageQuery,
  WorkspaceWebappPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import WebappLayout from "workspaces/layouts/WebappLayout";
import WebappFilesEditor from "webapps/features/WebappFilesEditor/WebappFilesEditor";
import VersionPicker from "webapps/features/VersionPicker/VersionPicker";
import useCacheKey from "core/hooks/useCacheKey";
import { WebappVersion_VersionFragment } from "webapps/graphql/queries.generated";
import { useUpdateWebappMutation } from "webapps/graphql/mutations.generated";

type Props = {
  webappSlug: string;
  workspaceSlug: string;
};

const WorkspaceWebappCodePage: NextPageWithLayout = (props: Props) => {
  const { webappSlug, workspaceSlug } = props;
  const { t } = useTranslation();
  const router = useRouter();
  const initialRef = router.query.ref as string | undefined;

  const { data, refetch } = useWorkspaceWebappPageQuery({
    variables: { workspaceSlug, webappSlug },
  });
  useCacheKey("webapps", refetch);

  const [selectedVersion, setSelectedVersion] =
    useState<WebappVersion_VersionFragment | null>(null);
  const [updateWebapp] = useUpdateWebappMutation();
  const [resolveProposal] = useResolveAssistantProposalMutation();
  const [isPublishing, setIsPublishing] = useState(false);

  const [proposedFiles, setProposedFiles] = useState<
    WebappProposedFile[] | null
  >(null);
  const [proposedToolInvocationId, setProposedToolInvocationId] = useState<
    string | null
  >(null);

  const handleProposedFiles = useCallback(
    (files: WebappProposedFile[] | null, toolInvocationId?: string) => {
      setProposedFiles(files);
      if (toolInvocationId !== undefined) {
        setProposedToolInvocationId(toolInvocationId);
      } else if (files !== null) {
        setProposedToolInvocationId(null);
      }
    },
    [],
  );

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

  const handleSaveSuccess = useCallback(() => {
    refetch().then();
    const idToResolve = proposedToolInvocationId;
    setProposedFiles(null);
    setProposedToolInvocationId(null);
    if (idToResolve) {
      resolveProposal({ variables: { toolInvocationId: idToResolve } });
    }
  }, [proposedToolInvocationId, resolveProposal, refetch]);

  const [isAssistantEnabled] = useFeature("assistant");
  const me = useMe();
  const aiEnabled = me?.user?.aiSettings?.enabled ?? false;
  const showAssistant = isAssistantEnabled && aiEnabled;

  const [chatOpen, setChatOpen] = useState(false);
  const [conversations, setConversations] = useState<WebappConversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<
    string | null
  >(null);

  const seededRef = useRef(false);
  useEffect(() => {
    if (seededRef.current || !data?.webapp) return;
    seededRef.current = true;
    const convs = data.webapp.assistantConversations ?? [];
    setConversations(convs);
    setActiveConversationId(convs[0]?.id ?? null);
    setChatOpen(convs.length > 0);
  }, [data?.webapp?.id]);

  const handleNewConversation = useCallback(() => {
    setActiveConversationId(null);
  }, []);

  const handleConversationCreated = useCallback(
    (conversation: WebappConversation) => {
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

  if (!data?.workspace || !data?.webapp) {
    return null;
  }

  const { workspace, webapp } = data;

  if (webapp.type !== WebappType.Static) {
    return null;
  }

  const source = webapp.source;
  const publishedVersionId =
    source?.__typename === "GitSource" ? source.publishedVersion : null;
  const isViewingPublished =
    !selectedVersion || selectedVersion.id === publishedVersionId;
  const monthlyLimitExceeded = data?.me?.assistantMonthlyLimitExceeded ?? false;

  const handlePublish = async () => {
    if (!selectedVersion || isPublishing) return;
    setIsPublishing(true);
    try {
      const { data: publishData } = await updateWebapp({
        variables: {
          input: { id: webapp.id, publishedVersionId: selectedVersion.id },
        },
        refetchQueries: ["WebappVersions"],
      });
      if (publishData?.updateWebapp?.success) {
        toast.success(t("Version published successfully"));
        refetch().then();
      } else {
        toast.error(t("Failed to publish version"));
      }
    } catch {
      toast.error(t("Failed to publish version"));
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <Page title={webapp.name}>
      <WebappLayout
        workspace={workspace}
        webapp={webapp}
        currentTab="code"
        extraActions={
          webapp.permissions.update && !isViewingPublished ? (
            <Button
              variant="primary"
              onClick={handlePublish}
              disabled={isPublishing}
              leadingIcon={isPublishing ? <Spinner size="xs" /> : undefined}
            >
              {isPublishing ? t("Publishing...") : t("Publish")}
            </Button>
          ) : undefined
        }
      >
        <DataCard.FormSection>
          <div className="flex items-center gap-3">
            <div className="w-96">
              <VersionPicker
                workspaceSlug={workspaceSlug}
                webappSlug={webappSlug}
                initialVersionId={initialRef}
                onChange={setSelectedVersion}
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
          {proposedFiles && (
            <AssistantProposalBanner
              label={t("Proposed changes from AI assistant")}
              onDismiss={handleDismiss}
              className="-my-2"
            />
          )}
          <div className="flex gap-4 min-h-[60vh] max-h-[65vh] overflow-hidden">
            <div className="relative flex-1 min-h-0">
              <WebappFilesEditor
                webappId={webapp.id}
                workspaceSlug={workspaceSlug}
                webappSlug={webappSlug}
                isEditable={webapp.permissions.update}
                versionRef={selectedVersion?.id}
                proposedFiles={proposedFiles ?? undefined}
                onSaveSuccess={handleSaveSuccess}
              />
            </div>
            {chatOpen && showAssistant && (
              <div className="w-[440px] shrink-0">
                <WebappEditChatPanel
                  webappId={webapp.id}
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
      </WebappLayout>
    </Page>
  );
};

WorkspaceWebappCodePage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WebappLayout.prefetch(ctx, client);
    const { data } = await client.query<
      WorkspaceWebappPageQuery,
      WorkspaceWebappPageQueryVariables
    >({
      query: WorkspaceWebappPageDocument,
      variables: {
        workspaceSlug: ctx.params!.workspaceSlug as string,
        webappSlug: ctx.params!.webappSlug as string,
      },
    });

    if (!data.workspace || !data.webapp) {
      return { notFound: true };
    }

    return {
      props: {
        workspaceSlug: ctx.params!.workspaceSlug,
        webappSlug: ctx.params!.webappSlug,
      },
    };
  },
});

export default WorkspaceWebappCodePage;
