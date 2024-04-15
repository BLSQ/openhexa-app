import Breadcrumbs from "core/components/Breadcrumbs";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import BackLayout from "core/layouts/back/BackLayout";
import DefaultLayout from "core/layouts/default";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import PipelineRunDataCard from "pipelines/features/PipelineRunDataCard";
import {
  PipelineRunPageDocument,
  PipelineRunPageQuery,
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
      <BackLayout title={""}>
        <Breadcrumbs className="my-8 px-2" withHome={false}>
          <Breadcrumbs.Part href="/pipelines" isFirst>
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
        <PipelineRunDataCard dag={dag} dagRun={dagRun} onRefresh={refetch} />
      </BackLayout>
    </Page>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  getServerSideProps: async (ctx, client) => {
    const { data } = await client.query<PipelineRunPageQuery>({
      query: PipelineRunPageDocument,
      variables: {
        pipelineId: ctx.params?.pipelineId as string,
        runId: ctx.params?.runId as string,
      },
    });
    if (!data.dagRun || !data.dag) {
      return {
        notFound: true,
      };
    }
  },
});

export default PipelineRunPage;
