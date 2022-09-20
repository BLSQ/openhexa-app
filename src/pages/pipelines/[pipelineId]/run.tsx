import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Page from "core/components/Layout/Page";
import { PageContent } from "core/components/Layout/PageContent";
import Title from "core/components/Title";
import { AlertType, displayAlert } from "core/helpers/alert";
import { createGetServerSideProps } from "core/helpers/page";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import PipelineRunForm from "pipelines/features/PipelineRunForm/PipelineRunForm";
import {
  PipelineConfigureRunPageDocument,
  usePipelineConfigureRunPageQuery,
} from "pipelines/graphql/queries.generated";
import { runPipeline } from "pipelines/helpers/pipeline";
import { getPipelineRun } from "pipelines/helpers/runs";
import ReactMarkdown from "react-markdown";

type Props = {
  run: Awaited<ReturnType<typeof getPipelineRun>>;
  pipelineId: string;
};

const PipelineConfigureRunPage = (props: Props) => {
  const { pipelineId, run } = props;
  const { t } = useTranslation();
  const router = useRouter();
  const { data } = usePipelineConfigureRunPageQuery({
    variables: { pipelineId },
  });

  const onSubmit = async (dagId: string, config: object) => {
    try {
      const { dag, dagRun } = await runPipeline(dagId, config);
      router.push({
        pathname: "/pipelines/[pipelineId]/runs/[runId]/",
        query: { pipelineId: dag.id, runId: dagRun.id },
      });
    } catch (err) {
      displayAlert(
        (err as Error).message ?? "An unexpected error ocurred.",
        AlertType.error
      );
    }
  };
  if (!data || !data.dag) {
    return null;
  }

  const { dag } = data;
  return (
    <Page title={t("Configure Pipeline")}>
      <PageContent>
        <Breadcrumbs className="my-8 px-2">
          <Breadcrumbs.Part href="/pipelines">
            {t("Data Pipelines")}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            href={{
              pathname: "/pipelines/[pipelineId]/run",
              query: { pipelineId: dag.id },
            }}
          >
            {t("Configure & Run")}
          </Breadcrumbs.Part>
        </Breadcrumbs>
        <Block>
          <Block.Content className="grid grid-cols-5 gap-4">
            <div className="col-span-3">
              <Title level={3}>
                {t("Create a new run of {{code}}", { code: dag.code })}
              </Title>

              <PipelineRunForm dag={dag} onSubmit={onSubmit} />
            </div>
            <div className="col-span-2">
              <Title level={3}>{t("Description")}</Title>
              {dag.template.description && (
                <ReactMarkdown className="prose max-w-3xl text-sm">
                  {dag.template.description}
                </ReactMarkdown>
              )}
            </div>
          </Block.Content>
        </Block>
      </PageContent>
    </Page>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  getServerSideProps: async (ctx, client) => {
    const pipelineId = ctx.params?.pipelineId as string;
    const fromRun = ctx.params?.fromRun as string | null;
    const { data } = await client.query({
      query: PipelineConfigureRunPageDocument,
      variables: { pipelineId },
    });

    if (!data.dag) {
      return {
        notFound: true,
      };
    }

    let run = null;
    if (fromRun) {
      run = await getPipelineRun(fromRun);
    }
    return {
      props: {
        pipelineId,
        run,
      },
    };
  },
});

export default PipelineConfigureRunPage;
