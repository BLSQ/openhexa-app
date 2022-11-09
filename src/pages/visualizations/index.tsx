import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import CountryColumn from "core/components/DataGrid/CountryColumn";
import DateColumn from "core/components/DataGrid/DateColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Page from "core/components/Layout/Page";
import { PageContent } from "core/components/Layout/PageContent";
import Link from "core/components/Link";
import { createGetServerSideProps } from "core/helpers/page";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import {
  VisualizationsPageDocument,
  VisualizationsPageQuery,
  VisualizationsPageQueryVariables,
  useVisualizationsPageQuery,
} from "visualizations/graphql/queries.generated";
import { useMemo } from "react";
import VisualizationPicture from "visualizations/features/VisualizationPicture";

type Props = {
  page: number;
  perPage: number;
};

const VisualizationsPage = (props: Props) => {
  const { t } = useTranslation();

  const router = useRouter();
  const { data } = useVisualizationsPageQuery({
    variables: {
      page: props.page,
      perPage: props.perPage,
    },
  });

  const onChangePage = ({ page }: { page: number }) => {
    router.push({ pathname: router.pathname, query: { page } });
  };

  if (!data) {
    return null;
  }

  return (
    <Page title={t("Visualizations")}>
      <PageContent>
        <Breadcrumbs className="my-8 px-2">
          <Breadcrumbs.Part href="/visualizations">
            {t("Visualizations")}
          </Breadcrumbs.Part>
        </Breadcrumbs>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-medium">{t("Visualizations")}</h2>
          </div>

          <Block>
            <DataGrid
              defaultPageSize={props.perPage}
              data={data.externalDashboards.items}
              totalItems={data.externalDashboards.totalItems}
              fetchData={onChangePage}
            >
              <BaseColumn id="name" label={t("Name")} minWidth={240}>
                {(item) => (
                  <a className="font-medium text-gray-700" href={item.url}>
                    <div className="flex items-center">
                      <VisualizationPicture visualization={item} />
                      <div className="ml-4 w-full truncate">
                        <div
                          className="truncate text-sm font-medium text-gray-900"
                          title={item.name}
                        >
                          {item.name}
                        </div>
                        <div className="truncate text-sm text-gray-500">
                          {item.url}
                        </div>
                      </div>
                    </div>
                  </a>
                )}
              </BaseColumn>
              <CountryColumn
                accessor="countries"
                label={t("Location")}
                max={1}
              />
              <DateColumn
                label={t("Updated at")}
                relative
                accessor="updatedAt"
              />
              <ChevronLinkColumn
                maxWidth="100"
                accessor="id"
                url={(value: any) => ({
                  pathname: "/visualizations/[visualizationId]",
                  query: { visualizationId: value },
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
    const page = (ctx.query.page as string)
      ? parseInt(ctx.query.page as string, 10)
      : 1;
    const perPage = 15;

    await client.query<
      VisualizationsPageQuery,
      VisualizationsPageQueryVariables
    >({
      query: VisualizationsPageDocument,
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

export default VisualizationsPage;
