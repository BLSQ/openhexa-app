import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Page from "core/components/Page";
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
import { useMemo } from "react";
import BackLayout from "core/layouts/back/BackLayout";
import { toast } from "react-toastify";
import MarkdownViewer from "core/components/MarkdownViewer";

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
      toast.error((err as Error).message ?? t("An unexpected error occurred."));
    }
  };
  const description = useMemo(
    () => data?.dag?.description || data?.dag?.template.description,
    [data],
  );
  if (!data || !data.dag) {
    return null;
  }

  const { dag } = data;

  return (
    <Page title={t("Configure Pipeline")}>
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
              pathname: "/pipelines/[pipelineId]/run",
              query: { pipelineId: dag.id },
            }}
          >
            {t("Configure & Run")}
          </Breadcrumbs.Part>
        </Breadcrumbs>
        <div className="flex flex-col gap-4 md:flex-row">
          <Block className="flex-1 shrink-0 basis-7/12">
            <Block.Header>
              {t("Create a new run of {{externalId}}", {
                externalId: dag.externalId,
              })}
            </Block.Header>
            <Block.Content>
              <PipelineRunForm
                fromConfig={run?.config}
                dag={dag}
                onSubmit={onSubmit}
              />
            </Block.Content>
          </Block>
          {description && (
            <Block className="basis-5/12">
              <Block.Header>{t("Description")}</Block.Header>
              <Block.Content>
                <MarkdownViewer
                  className="prose max-w-3xl text-sm"
                  markdown={description}
                />
              </Block.Content>
            </Block>
          )}
        </div>
      </BackLayout>
    </Page>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  getServerSideProps: async (ctx, client) => {
    const pipelineId = ctx.params?.pipelineId as string;
    const fromRun = ctx.query?.fromRun as string | null;
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
      run = await getPipelineRun(fromRun, ctx.req);
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
