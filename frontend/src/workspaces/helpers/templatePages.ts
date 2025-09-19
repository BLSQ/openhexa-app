import { GetServerSidePropsContext, GetServerSidePropsResult } from "next";
import { CustomApolloClient } from "core/helpers/apollo";
import {
  WorkspaceTemplatePageDocument,
  WorkspaceTemplatePageQuery,
  WorkspaceTemplatePageQueryVariables,
} from "workspaces/graphql/queries.generated";
import TemplateLayout from "workspaces/layouts/TemplateLayout";

type TemplatePageProps = {
  workspaceSlug: string;
  templateCode: string;
};

export const createTemplatePageServerSideProps = () => ({
  requireAuth: true,
  async getServerSideProps(
    ctx: GetServerSidePropsContext,
    client: CustomApolloClient,
  ): Promise<GetServerSidePropsResult<TemplatePageProps>> {
    await TemplateLayout.prefetch(ctx, client);
    const { data } = await client.query<
      WorkspaceTemplatePageQuery,
      WorkspaceTemplatePageQueryVariables
    >({
      query: WorkspaceTemplatePageDocument,
      variables: {
        workspaceSlug: ctx.params!.workspaceSlug as string,
        templateCode: ctx.params!.templateCode as string,
      },
    });

    if (!data.workspace || !data.template) {
      return { notFound: true };
    }
    return {
      props: {
        workspaceSlug: ctx.params!.workspaceSlug as string,
        templateCode: ctx.params!.templateCode as string,
      },
    };
  },
});
