import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import DataGrid from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import CountryColumn from "core/components/DataGrid/CountryColumn";
import DateColumn from "core/components/DataGrid/DateColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Page from "core/components/Layout/Page";
import { PageContent } from "core/components/Layout/PageContent";
import { createGetServerSideProps } from "core/helpers/page";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import {
  PipelinesPageDocument,
  usePipelinesPageQuery,
} from "pipelines/graphql/queries.generated";
import { formatDAGRunStatus } from "pipelines/helpers/format";
import { useMemo } from "react";

type Props = {
  page: number;
  perPage: number;
};

const PipelinesPage = (props: Props) => {
  const { t } = useTranslation();

  const router = useRouter();
  const { data } = usePipelinesPageQuery();

  const onChangePage = ({ page }: { page: number }) => {
    router.push({ pathname: router.pathname, query: { page } });
  };

  const items = useMemo(() => {
    return (
      data?.dags.items.map((dag) => {
        return {
          ...dag,
          lastRun: dag.runs.items?.length > 0 ? dag.runs.items[0] : null,
        };
      }) ?? []
    );
  }, [data]);

  if (!data) {
    return null;
  }

  return (
    <Page title={t("Pipelines")}>
      <PageContent>
        <Breadcrumbs className="my-8 px-2">
          <Breadcrumbs.Part href="/pipelines">
            {t("Data Pipelines")}
          </Breadcrumbs.Part>
        </Breadcrumbs>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-medium">{t("Pipelines")}</h2>
          </div>

          <Block>
            <DataGrid
              defaultPageSize={15}
              data={items}
              totalItems={data.dags.totalItems}
              totalPages={data.dags.totalPages}
              fetchData={onChangePage}
            >
              <TextColumn
                id="label"
                label={t("Name")}
                textPath="label"
                textClassName="text-gray-700 font-medium"
                url={(value: any) => ({
                  pathname: "/pipelines/[pipelinesId]",
                  query: { pipelinesId: value.id },
                })}
                minWidth={240}
              />
              <CountryColumn accessor="countries" label={t("Location")} />
              <DateColumn
                label={t("Last run")}
                relative
                accessor="lastRun.executionDate"
              />
              <TextColumn
                label={t("Last status")}
                accessor={(value) =>
                  value.lastRun ? (
                    <PipelineRunStatusBadge dagRun={value.lastRun} />
                  ) : (
                    "-"
                  )
                }
              />
              <ChevronLinkColumn
                maxWidth="100"
                accessor="id"
                url={(value: any) => ({
                  pathname: "/pipelines/[pipelineId]",
                  query: { pipelineId: value },
                })}
              />
            </DataGrid>
          </Block>
        </div>
      </PageContent>
    </Page>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  getServerSideProps: async (ctx, client) => {
    await client.query({
      query: PipelinesPageDocument,
    });
  },
});

export default PipelinesPage;
