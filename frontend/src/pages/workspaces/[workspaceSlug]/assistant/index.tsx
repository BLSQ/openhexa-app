import { gql, useQuery } from "@apollo/client";
import Breadcrumbs from "core/components/Breadcrumbs";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import AssistantChat from "assistant/features/AssistantChat";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

const WORKSPACE_ASSISTANT_QUERY = gql`
  query WorkspaceAssistantPage($workspaceSlug: String!) {
    workspace(slug: $workspaceSlug) {
      slug
      name
      permissions {
        update
      }
      ...WorkspaceLayout_workspace
    }
  }
  ${WorkspaceLayout.fragments.workspace}
`;

type Props = {
  workspaceSlug: string;
};

const WorkspaceAssistantPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const { data } = useQuery(WORKSPACE_ASSISTANT_QUERY, {
    variables: { workspaceSlug: props.workspaceSlug },
  });

  if (!data?.workspace) {
    return null;
  }

  const { workspace } = data;

  return (
    <Page title={`${workspace.name} - ${t("Assistant")}`}>
      <WorkspaceLayout
        workspace={workspace}
        header={
          <Breadcrumbs withHome={false}>
            <Breadcrumbs.Part
              isFirst
              isLast
              href={`/workspaces/${encodeURIComponent(workspace.slug)}/assistant`}
            >
              {t("Assistant")}
            </Breadcrumbs.Part>
          </Breadcrumbs>
        }
      >
        <WorkspaceLayout.PageContent>
          <AssistantChat workspaceSlug={workspace.slug} />
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
    </Page>
  );
};

WorkspaceAssistantPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WorkspaceLayout.prefetch(ctx, client);
    const { data } = await client.query({
      query: WORKSPACE_ASSISTANT_QUERY,
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
      props: {
        workspaceSlug: data.workspace.slug,
      },
    };
  },
});

export default WorkspaceAssistantPage;
