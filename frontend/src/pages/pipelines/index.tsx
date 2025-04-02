import Block from "core/components/Block";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import CountryColumn from "core/components/DataGrid/CountryColumn";
import DateColumn from "core/components/DataGrid/DateColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Page from "core/components/Page";
import Link from "core/components/Link";
import { createGetServerSideProps } from "core/helpers/page";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import {
  PipelinesPageDocument,
  PipelinesPageQuery,
  PipelinesPageQueryVariables,
  usePipelinesPageQuery,
} from "pipelines/graphql/queries.generated";
import { useMemo } from "react";
import BackLayout from "core/layouts/back/BackLayout";
import Button from "core/components/Button";

type Props = {
  page: number;
  perPage: number;
};

const PipelinesPage = (props: Props) => {
  const { t } = useTranslation();

  const router = useRouter();
  const { data } = usePipelinesPageQuery({
    variables: {
      page: props.page,
      perPage: props.perPage,
    },
  });

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
    <Page title={t("Airflow Pipelines")}>
      <BackLayout
        title={
          <div className="flex gap-2">
            <Button onClick={() => router.push("/pipelines")} size="sm">
              {t("Airflow Pipelines")}
            </Button>
            <Button
              onClick={() => router.push("/notebooks")}
              variant="white"
              size="sm"
            >
              {t("Notebooks")}
            </Button>
          </div>
        }
      >
        <Block>
          <DataGrid
            defaultPageSize={props.perPage}
            data={items}
            totalItems={data.dags.totalItems}
            fetchData={onChangePage}
          >
            <BaseColumn id="name" label={t("Name")} minWidth={240}>
              {(item) => (
                <Link
                  customStyle="text-gray-700 font-medium"
                  href={{
                    pathname: "/pipelines/[pipelinesId]",
                    query: { pipelinesId: item.id },
                  }}
                >
                  {item.label || item.externalId}
                </Link>
              )}
            </BaseColumn>
            <CountryColumn accessor="countries" label={t("Location")} max={1} />
            <DateColumn
              label={t("Last run")}
              relative
              accessor="lastRun.executionDate"
            />
            <TextColumn
              label={t("Last status")}
              accessor={(value) =>
                value.lastRun ? (
                  <PipelineRunStatusBadge run={value.lastRun} />
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
      </BackLayout>
    </Page>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  getServerSideProps: async (ctx, client) => {
    const page = (ctx.query.page as string)
      ? parseInt(ctx.query.page as string, 10)
      : 1;
    const perPage = 15;

    await client.query<PipelinesPageQuery, PipelinesPageQueryVariables>({
      query: PipelinesPageDocument,
      variables: {
        page,
        perPage,
      },
    });
    return {
      props: {
        page,
        perPage,
      },
    };
  },
});

export default PipelinesPage;
