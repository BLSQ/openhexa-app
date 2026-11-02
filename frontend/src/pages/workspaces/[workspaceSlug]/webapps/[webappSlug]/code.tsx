import { SparklesIcon } from "@heroicons/react/24/outline";
import WebappEditChatPanel, {
  WebappConversation,
} from "assistant/features/WebappEditChatPanel";
import Button from "core/components/Button";
import DataCard from "core/components/DataCard";
import Page from "core/components/Page";
import Spinner from "core/components/Spinner";
import SubscriptionLimitTooltip from "core/components/SubscriptionLimitTooltip";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
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
import GitClonePopover from "webapps/features/GitClonePopover/GitClonePopover";
import RestoreWebappVersionDialog from "webapps/features/RestoreWebappVersionDialog/RestoreWebappVersionDialog";
import useCacheKey from "core/hooks/useCacheKey";
import {
  useWebappVersionsQuery,
  WebappVersion_VersionFragment,
} from "webapps/graphql/queries.generated";
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
  const [isPublishing, setIsPublishing] = useState(false);
  const [restoreTarget, setRestoreTarget] = useState<string | null>(null);
  const [isEditorBusy, setIsEditorBusy] = useState(false);
  const [versionPickerKey, setVersionPickerKey] = useState(0);

  const { data: versionsData, refetch: refetchVersions } =
    useWebappVersionsQuery({
      variables: { workspaceSlug, webappSlug, page: 1, perPage: 1 },
    });
  const latestVersionId = versionsData?.webapp?.versions?.items?.[0]?.id;

  // A new version was committed (editor save or assistant): show it.
  const handleVersionSaved = useCallback(() => {
    refetch().then();
    refetchVersions().then();
    setSelectedVersion(null);
    setVersionPickerKey((k) => k + 1);
  }, [refetch, refetchVersions]);

  const showAssistant =
    data?.workspace?.organization?.aiSettings?.enabled ?? false;
  const aiBudgetLimitReached =
    data?.workspace?.organization?.aiBudgetLimitReached ?? false;

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
    setChatOpen(convs.length > 0 && !aiBudgetLimitReached);
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
  const repositoryUrl =
    source?.__typename === "GitSource" ? source.repositoryUrl : null;
  const selectedVersionId = selectedVersion?.id ?? latestVersionId ?? null;
  const isViewingLatest =
    !selectedVersionId || selectedVersionId === latestVersionId;
  const isViewingPublished = selectedVersionId === publishedVersionId;

  // Only the latest version can be published; an older one is brought back as
  // a new latest version (and published) instead.
  const handlePublish = async () => {
    if (!latestVersionId || isPublishing) return;
    setIsPublishing(true);
    try {
      const { data: publishData } = await updateWebapp({
        variables: {
          input: { id: webapp.id, publishedVersionId: latestVersionId },
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

  const extraAction =
    !webapp.permissions.update || isEditorBusy ? undefined : isViewingLatest ? (
      !isViewingPublished && (
        <Button
          variant="primary"
          onClick={handlePublish}
          disabled={isPublishing}
          leadingIcon={isPublishing ? <Spinner size="xs" /> : undefined}
        >
          {isPublishing ? t("Publishing...") : t("Publish")}
        </Button>
      )
    ) : (
      <Button
        variant="primary"
        onClick={() => selectedVersionId && setRestoreTarget(selectedVersionId)}
      >
        {t("Roll back to this version")}
      </Button>
    );

  return (
    <Page title={webapp.name}>
      <WebappLayout
        workspace={workspace}
        webapp={webapp}
        currentTab="code"
        extraActions={extraAction || undefined}
      >
        <DataCard.FormSection>
          <div className="flex items-center gap-3">
            <div className="w-96">
              <VersionPicker
                key={versionPickerKey}
                workspaceSlug={workspaceSlug}
                webappSlug={webappSlug}
                initialVersionId={initialRef}
                onChange={setSelectedVersion}
              />
            </div>
            <div className="ml-auto flex items-center gap-2">
              {repositoryUrl && (
                <GitClonePopover repositoryUrl={repositoryUrl} />
              )}
              {showAssistant && (
                <SubscriptionLimitTooltip
                  isLimitReached={aiBudgetLimitReached}
                  title={t("Monthly AI budget reached")}
                >
                  <Button
                    onClick={() => setChatOpen((o) => !o)}
                    variant="secondary"
                    size="md"
                    leadingIcon={<SparklesIcon className="h-4 w-4" />}
                  >
                    {t("AI Assistant")}
                  </Button>
                </SubscriptionLimitTooltip>
              )}
            </div>
          </div>
          <div className="flex gap-4 min-h-[60vh] max-h-[65vh] overflow-hidden">
            <div className="relative flex-1 min-h-0">
              <WebappFilesEditor
                webappId={webapp.id}
                workspaceSlug={workspaceSlug}
                webappSlug={webappSlug}
                isEditable={webapp.permissions.update && isViewingLatest}
                versionRef={selectedVersion?.id}
                onSaveSuccess={handleVersionSaved}
                onBusyChange={setIsEditorBusy}
              />
            </div>
            {chatOpen && showAssistant && (
              <div className="w-[440px] shrink-0">
                <WebappEditChatPanel
                  webappId={webapp.id}
                  workspaceSlug={workspaceSlug}
                  onVersionSaved={handleVersionSaved}
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
        <RestoreWebappVersionDialog
          open={restoreTarget !== null}
          onClose={() => setRestoreTarget(null)}
          webappId={webapp.id}
          versionId={restoreTarget}
          onRestored={handleVersionSaved}
        />
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
