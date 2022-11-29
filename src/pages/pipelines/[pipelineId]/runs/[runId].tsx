import Breadcrumbs from "core/components/Breadcrumbs";
import Page from "core/components/Page";
import DefaultLayout from "core/layouts/default";
import { createGetServerSideProps } from "core/helpers/page";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import PipelineRunDataCard from "pipelines/features/PipelineRunDataCard";
import {
  PipelineRunPageDocument,
  usePipelineRunPageQuery,
} from "pipelines/graphql/queries.generated";
import { getPipelineRunLabel } from "pipelines/helpers/runs";

type Props = {
  page: number;
  perPage: number;
};

const PipelineRunPage = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();

  const { data, refetch } = usePipelineRunPageQuery({
    variables: {
      pipelineId: router.query.pipelineId as string,
      runId: router.query.runId as string,
    },
  });

  if (!data || !data.dag || !data.dagRun) {
    return null;
  }

  const { dagRun, dag } = data;

  return (
    <Page title={t("Pipeline Run")}>
      <DefaultLayout.PageContent>
        <Breadcrumbs className="my-8 px-2">
          <Breadcrumbs.Part href="/pipelines">
            {t("Data Pipelines")}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            href={{
              pathname: "/pipelines/[pipelineId]",
              query: { pipelineId: dag.id },
            }}
          >
            {dag.label || dag.externalId}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            href={{
              pathname: "/pipelines/[pipelineId]/runs/[runId]",
              query: { pipelineId: dag.id, runId: dagRun.id },
            }}
          >
            {getPipelineRunLabel(dagRun, dag)}
          </Breadcrumbs.Part>
        </Breadcrumbs>
        <div className="space-y-12">
          <PipelineRunDataCard dag={dag} dagRun={dagRun} onRefresh={refetch} />
        </div>
      </DefaultLayout.PageContent>
    </Page>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  getServerSideProps: async (ctx, client) => {
    const { data } = await client.query({
      query: PipelineRunPageDocument,
      variables: {
        pipelineId: ctx.params?.pipelineId as string,
        runId: ctx.params?.runId as string,
      },
    });
    if (!data.dagRun) {
      return {
        notFound: true,
      };
    }
  },
});

export default PipelineRunPage;
