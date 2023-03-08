import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Page from "core/components/Page";
import Title from "core/components/Title";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { capitalize } from "lodash";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import IHPForm from "pipelines/features/PipelineRunForm/IHPForm";
import {
  useWorkspacePipelineStartPageQuery,
  WorkspacePipelineStartPageDocument,
} from "workspaces/graphql/queries.generated";
import { FAKE_WORKSPACE } from "workspaces/helpers/fixtures";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  perPage: number;
};

const WorkspacePipelineRunPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const { data } = useWorkspacePipelineStartPageQuery({
    variables: { workspaceSlug: router.query.workspaceSlug as string },
  });

  if (!data?.workspace) {
    return null;
  }
  const { workspace } = data;

  const dag = FAKE_WORKSPACE.dags.find((d) => d.id === router.query.pipelineId);

  if (!dag) {
    return null;
  }

  return (
    <Page title={t("Workspace")}>
      <WorkspaceLayout workspace={workspace}>
        <WorkspaceLayout.Header>
          <Breadcrumbs withHome={false}>
            <Breadcrumbs.Part
              isFirst
              href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
            >
              {workspace.name}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              href={`/workspaces/${encodeURIComponent(
                workspace.slug
              )}/pipelines`}
            >
              {t("Pipelines")}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              href={`/workspaces/${encodeURIComponent(
                workspace.slug
              )}/pipelines/${encodeURIComponent(dag.id)}`}
            >
              {dag.label}
            </Breadcrumbs.Part>
          </Breadcrumbs>
        </WorkspaceLayout.Header>
        <WorkspaceLayout.PageContent>
          <Block className="p-4">
            <div>
              <Title level={2}>{capitalize(dag.label)}</Title>
              <p className="truncate text-sm text-gray-700">
                {dag.description}
              </p>
            </div>
            <div className="mt-5 grid grid-cols-3 sm:grid-cols-3 ">
              <div className="col-span-2 border-2 border-solid p-2 ">
                <IHPForm />
              </div>
              <div className="border-2 border-solid p-4">
                <div>
                  <Title level={5}>{t("Usage")}</Title>
                  <p>{dag.description}</p>
                </div>
                <div className="mt-5">
                  <Title level={5}>{t("Parameters")}</Title>
                  <p>Parameter 1 : Definition 1</p>
                  <p>Parameter 2 : Definition 2</p>
                </div>
              </div>
            </div>
          </Block>
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
    </Page>
  );
};

WorkspacePipelineRunPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    const { data } = await client.query({
      query: WorkspacePipelineStartPageDocument,
      variables: { workspaceSlug: ctx.params?.workspaceSlug },
    });
    await WorkspaceLayout.prefetch(client);

    const dag = FAKE_WORKSPACE.dags.find(
      (d) => d.id === ctx.params?.pipelineId
    );

    if (!data.workspace || !dag) {
      return {
        notFound: true,
      };
    }
  },
});

export default WorkspacePipelineRunPage;
