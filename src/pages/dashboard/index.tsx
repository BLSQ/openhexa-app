import Breadcrumbs from "core/components/Breadcrumbs";
import Block from "core/components/Block";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import DateColumn from "core/components/DataGrid/DateColumn";
import Page from "core/components/Layout/Page";
import { PageContent } from "core/components/Layout/PageContent";
import { createGetServerSideProps } from "core/helpers/page";
import {
  DashboardPageDocument,
  useDashboardPageQuery,
} from "dashboards/graphql/queries.generated";
import { useTranslation } from "next-i18next";
import {
  BeakerIcon,
  BookmarkSquareIcon,
  BookOpenIcon,
} from "@heroicons/react/24/outline";
import { ActivityStatus } from "graphql-types";
import Badge from "core/components/Badge";
import { useMemo } from "react";
import clsx from "clsx";
import Title from "core/components/Title";
import Link from "core/components/Link";
import { TextColumn } from "core/components/DataGrid/TextColumn";

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

  const label = (() => {
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
  })();

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
      <PageContent>
        <Breadcrumbs className="my-8 px-2">
          <Breadcrumbs.Part href="/dashboard">
            {t("Dashboard")}
          </Breadcrumbs.Part>
        </Breadcrumbs>
        <div className="my-12">
          <Title level={3} className="text-lg font-medium text-black">
            {t("Overview")}
          </Title>
          <div className="mt-4">
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
              <Block>
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <BookmarkSquareIcon className="text-cool-gray-400 h-6 w-6" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt>
                          <div className="text-cool-gray-500 truncate text-sm font-medium leading-5">
                            {t("Datasources")}
                          </div>
                        </dt>
                        <dd>
                          <div className="text-cool-gray-900 text-lg font-medium leading-7">
                            {data?.catalog.totalItems}
                          </div>
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
                <div className="bg-cool-gray-50 px-5 py-3">
                  <div className="text-sm leading-5">
                    <Link
                      href="/catalog"
                      className="font-medium text-blue-600 transition duration-150 ease-in-out hover:text-blue-900"
                    >
                      {t("View all")}
                    </Link>
                  </div>
                </div>
              </Block>
              <Block>
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <BookOpenIcon className="text-cool-gray-400 h-6 w-6" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt>
                          <div className="text-cool-gray-500 truncate text-sm font-medium leading-5">
                            {t("Notebooks")}
                          </div>
                        </dt>
                        <dd>
                          <div className="text-cool-gray-900 text-lg font-medium leading-7">
                            {data?.totalNotebooks}
                          </div>
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
                <div className="bg-cool-gray-50 px-5 py-3">
                  <div className="text-sm leading-5">
                    <Link
                      href="/notebooks"
                      className="font-medium text-blue-600 transition duration-150 ease-in-out hover:text-blue-900"
                    >
                      {t("View all")}
                    </Link>
                  </div>
                </div>
              </Block>
              <Block>
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <BeakerIcon className="text-cool-gray-400 h-6 w-6" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt>
                          <div className="text-cool-gray-500 truncate text-sm font-medium leading-5">
                            {t("Pipelines")}
                          </div>
                        </dt>
                        <dd>
                          <div className="text-cool-gray-900 text-lg font-medium leading-7">
                            {data?.dags.totalItems}
                          </div>
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
                <div className="bg-cool-gray-50 px-5 py-3">
                  <div className="text-sm leading-5">
                    <Link
                      href="/pipelines"
                      className="font-medium text-blue-600 transition duration-150 ease-in-out hover:text-blue-900"
                    >
                      {t("View all")}
                    </Link>
                  </div>
                </div>
              </Block>
            </div>
          </div>

          <div className="my-12">
            <Title
              level={4}
              className="text-lg font-medium leading-6 text-gray-700"
            >
              {t("Last Activity")}
            </Title>
            <div className="mt-4">
              <Block>
                <DataGrid data={data?.lastActivities || []}>
                  <TextColumn
                    id="name"
                    label={t("Name")}
                    accessor="description"
                    maxWidth={200}
                    className="truncate text-sm text-gray-900"
                  />

                  <BaseColumn id="status" label={t("Status")}>
                    {(item) => <ActivityStatusBadge status={item.status} />}
                  </BaseColumn>

                  <DateColumn
                    label={t("Date")}
                    relative
                    accessor="occurredAt"
                  />
                  <ChevronLinkColumn
                    accessor="url"
                    url={(value: any) => ({
                      pathname: value,
                    })}
                  />
                </DataGrid>
              </Block>
            </div>
          </div>
        </div>
      </PageContent>
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
