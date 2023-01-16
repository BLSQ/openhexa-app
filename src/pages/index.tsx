import {
  BeakerIcon,
  BookOpenIcon,
  CircleStackIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import Badge from "core/components/Badge";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import DateColumn from "core/components/DataGrid/DateColumn";
import Page from "core/components/Page";
import Stats from "core/components/Stats";
import Title from "core/components/Title";
import { createGetServerSideProps } from "core/helpers/page";
import DefaultLayout from "core/layouts/default";
import {
  DashboardPageDocument,
  useDashboardPageQuery,
} from "dashboards/graphql/queries.generated";
import { ActivityStatus } from "graphql-types";
import { useTranslation } from "next-i18next";
import { useMemo } from "react";

const ActivityStatusBadge = ({ status }: { status: ActivityStatus }) => {
  const { t } = useTranslation();
  let className = useMemo(() => {
    switch (status) {
      case ActivityStatus.Error:
        return "bg-red-100 text-red-500";
      case ActivityStatus.Pending:
        return "bg-gray-100 text-gray-600";
      case ActivityStatus.Running:
        return "bg-sky-100 text-sky-600";
      case ActivityStatus.Success:
        return "bg-emerald-50 text-emerald-500";
    }
  }, [status]);

  const label = useMemo(() => {
    switch (status) {
      case ActivityStatus.Error:
        return t("Error");
      case ActivityStatus.Pending:
        return t("Pending");
      case ActivityStatus.Running:
        return t("Running");
      case ActivityStatus.Success:
        return t("Succeeded");
    }
  }, [status, t]);

  return (
    <Badge className={clsx(className, "flex items-center")}>{label}</Badge>
  );
};

const DashboardPage = () => {
  const { t } = useTranslation();
  const { data } = useDashboardPageQuery();
  if (!data) {
    return null;
  }

  return (
    <Page title={t("Dashboard")}>
      <DefaultLayout.PageContent>
        <Breadcrumbs className="my-8 px-2">
          <Breadcrumbs.Part href="/dashboard">
            {t("Dashboard")}
          </Breadcrumbs.Part>
        </Breadcrumbs>

        <div>
          <Title level={2} className="text-gray-700">
            {t("Overview")}
          </Title>

          <div className="grid grid-cols-2 gap-5 sm:grid-cols-3">
            <Stats
              count={data.catalog.totalItems}
              url="/catalog"
              label={t("Datasources")}
              icon={<CircleStackIcon className="h-8 w-8" />}
            />

            <Stats
              count={data.totalNotebooks}
              url="/notebooks"
              label={t("Notebooks")}
              icon={<BookOpenIcon className="h-8 w-8" />}
            />

            <Stats
              count={data.dags.totalItems}
              url="/pipelines"
              label={t("Pipelines")}
              icon={<BeakerIcon className="h-8 w-8" />}
            />
          </div>
        </div>

        <div className="mt-12">
          <Title level={2} className="text-gray-700">
            {t("Last Activity")}
          </Title>

          <Block>
            <DataGrid data={data.lastActivities} fixedLayout={false}>
              <BaseColumn
                id="description"
                label={t("Name")}
                accessor="description"
                className="max-w-[250px] text-sm text-gray-900 lg:max-w-[400px]"
              >
                {(value) => (
                  <div
                    className="truncate"
                    dangerouslySetInnerHTML={{ __html: value }}
                  ></div>
                )}
              </BaseColumn>

              <BaseColumn id="status" label={t("Status")}>
                {(item) => <ActivityStatusBadge status={item.status} />}
              </BaseColumn>
              <DateColumn label={t("Date")} relative accessor="occurredAt" />
              <ChevronLinkColumn
                accessor="url"
                url={(value: any) => ({
                  pathname: value,
                })}
              />
            </DataGrid>
          </Block>
        </div>
      </DefaultLayout.PageContent>
    </Page>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  getServerSideProps: async (ctx, client) => {
    await client.query({
      query: DashboardPageDocument,
    });
  },
});

export default DashboardPage;
