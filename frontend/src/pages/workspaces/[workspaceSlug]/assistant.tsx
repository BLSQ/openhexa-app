import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useEffect, useState } from "react";
import ChatPane from "assistant/features/ChatPane";
import ConversationList from "assistant/features/ConversationList";
import {
  AssistantPageDocument,
  AssistantPageQuery,
  useAssistantPageQuery,
} from "assistant/graphql/queries.generated";
import { useCreateAssistantConversationMutation } from "assistant/graphql/mutations.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  workspaceSlug: string;
};

const AssistantPage: NextPageWithLayout<Props> = ({ workspaceSlug }) => {
  const [selectedConversationId, setSelectedConversationId] = useState<
    string | null
  >(null);

  const { data, refetch: refetchPage } = useAssistantPageQuery({
    variables: { workspaceSlug },
  });

  const conversations = data?.workspace?.assistantConversations ?? [];

  useEffect(() => {
    if (!selectedConversationId && conversations.length > 0) {
      setSelectedConversationId(conversations[0].id);
    }
  }, [conversations, selectedConversationId]);

  const [createConversation, { loading: creating }] =
    useCreateAssistantConversationMutation({
      onCompleted: (result) => {
        const newConv = result.createAssistantConversation;
        if (newConv) {
          setSelectedConversationId(newConv.id);
          refetchPage();
        }
      },
    });

  const handleNewConversation = () => {
    createConversation({
      variables: { input: { workspaceSlug } },
    });
  };

  if (!data?.workspace) {
    return null;
  }

  return (
    <Page title="Assistant">
      <WorkspaceLayout workspace={data.workspace} withMarginBottom={false}>
        <div className="flex h-screen overflow-hidden">
          <ConversationList
            conversations={conversations}
            selectedId={selectedConversationId}
            onSelect={setSelectedConversationId}
            onNew={handleNewConversation}
            creating={creating}
          />
          <ChatPane conversationId={selectedConversationId} />
        </div>
      </WorkspaceLayout>
    </Page>
  );
};

AssistantPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WorkspaceLayout.prefetch(ctx, client);
    const { data } = await client.query<AssistantPageQuery>({
      query: AssistantPageDocument,
      variables: { workspaceSlug: ctx.params?.workspaceSlug },
    });

    if (!data.workspace) {
      return { notFound: true };
    }

    return {
      props: { workspaceSlug: ctx.params?.workspaceSlug },
    };
  },
});

export default AssistantPage;
