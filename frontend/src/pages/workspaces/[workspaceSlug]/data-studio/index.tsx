import { SparklesIcon } from "@heroicons/react/24/outline";
import SavedQueryChatPanel, {
  SavedQueryConversation,
} from "assistant/features/SavedQueryChatPanel";
import DetailShell, {
  AssistantDock,
  useAssistantDock,
} from "core/components/DetailShell";
import Page from "core/components/Page";
import SubscriptionLimitTooltip from "core/components/SubscriptionLimitTooltip";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useCallback, useRef, useState } from "react";
import DataStudioEditor from "workspaces/features/DataStudioEditor";
import { DataStudioEditorHandle } from "workspaces/features/DataStudioEditor/DataStudioEditor";
import {
  useWorkspaceDataStudioPageQuery,
  WorkspaceDataStudioPageDocument,
} from "workspaces/graphql/queries.generated";
import DataStudioLayout from "workspaces/layouts/DataStudioLayout";

const ASSISTANT_STORAGE_KEY = "data-studio-assistant";

type Props = {
  workspaceSlug: string;
};

const WorkspaceDataStudioPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const { data } = useWorkspaceDataStudioPageQuery({
    variables: { workspaceSlug: props.workspaceSlug },
  });
  const editorRef = useRef<DataStudioEditorHandle>(null);

  // The blank editor has no saved query to link a conversation to, so its
  // conversations only live as long as the page: the assistant drafts SQL into
  // the buffer and the user decides what to save.
  const [conversations, setConversations] = useState<SavedQueryConversation[]>(
    [],
  );
  const [activeConversationId, setActiveConversationId] = useState<
    string | null
  >(null);
  const { isOpen: isAssistantOpen, toggle: toggleAssistant } = useAssistantDock(
    ASSISTANT_STORAGE_KEY,
  );
  const handleDraftSql = useCallback((sql: string) => {
    editorRef.current?.setContent(sql);
  }, []);

  if (!data?.workspace) {
    return null;
  }
  const { workspace } = data;
  const aiEnabled = workspace.organization?.aiSettings?.enabled ?? false;
  const aiBudgetLimitReached =
    workspace.organization?.aiBudgetLimitReached ?? false;

  return (
    <Page title={t("Data Studio")}>
      <DataStudioLayout workspace={workspace} currentTab="editor">
        <DetailShell>
          <DetailShell.Body>
            <DetailShell.Main>
              {/* Full-bleed IDE: fill the area below the header and sub-nav. */}
              <div className="h-full min-h-0 p-4">
                <DataStudioEditor
                  ref={editorRef}
                  workspaceSlug={workspace.slug}
                  canCreate={workspace.permissions.createSavedQuery}
                  toolbarExtra={
                    aiEnabled &&
                    !isAssistantOpen && (
                      <SubscriptionLimitTooltip
                        isLimitReached={aiBudgetLimitReached}
                        title={t("Monthly AI budget reached")}
                      >
                        <button
                          onClick={toggleAssistant}
                          disabled={aiBudgetLimitReached}
                          className="inline-flex h-8 items-center gap-1.5 rounded-md bg-indigo-100 px-2.5 text-xs font-medium text-indigo-700 hover:bg-indigo-200 disabled:cursor-not-allowed disabled:bg-transparent disabled:text-gray-300"
                        >
                          <SparklesIcon className="h-4 w-4" />
                          {t("AI Assistant")}
                        </button>
                      </SubscriptionLimitTooltip>
                    )
                  }
                />
              </div>
            </DetailShell.Main>
            {aiEnabled && isAssistantOpen && (
              <AssistantDock storageKey={ASSISTANT_STORAGE_KEY}>
                <SavedQueryChatPanel
                  workspaceSlug={workspace.slug}
                  savedQueryId={null}
                  onDraftSql={handleDraftSql}
                  conversations={conversations}
                  activeConversationId={activeConversationId}
                  onConversationChange={setActiveConversationId}
                  onNewConversation={() => setActiveConversationId(null)}
                  onConversationCreated={(conversation) => {
                    setConversations((prev) => [conversation, ...prev]);
                    setActiveConversationId(conversation.id);
                  }}
                  onConversationNameChange={(id, conversationName) =>
                    setConversations((prev) =>
                      prev.map((c) =>
                        c.id === id ? { ...c, name: conversationName } : c,
                      ),
                    )
                  }
                  flush
                  onClose={toggleAssistant}
                />
              </AssistantDock>
            )}
          </DetailShell.Body>
        </DetailShell>
      </DataStudioLayout>
    </Page>
  );
};

WorkspaceDataStudioPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await DataStudioLayout.prefetch(ctx, client);
    const { data } = await client.query({
      query: WorkspaceDataStudioPageDocument,
      variables: {
        workspaceSlug: ctx.params?.workspaceSlug,
      },
    });

    if (!data.workspace) {
      return {
        notFound: true,
      };
    }
    return {
      props: { workspaceSlug: data.workspace.slug },
    };
  },
});

export default WorkspaceDataStudioPage;
