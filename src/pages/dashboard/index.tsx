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
import { BookmarkSquareIcon, BookOpenIcon } from "@heroicons/react/24/outline";
import DescriptionList, {
  DescriptionListDisplayMode,
} from "core/components/DescriptionList";
import Link from "next/link";
import { ActivityStatus } from "graphql-types";
import Badge from "core/components/Badge";
import { useMemo } from "react";
import clsx from "clsx";
import { capitalize } from "lodash";

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
  return (
    <Badge className={clsx(className, "flex items-center")}>
      {t(capitalize(status))}
    </Badge>
  );
};

const dummy = [
  {
    description: "All datasources are up to date!",
    occurredAt: "2022-11-09T00:00:39.651Z",
    url: "/catalog/",
    status: "ERROR",
  },
  {
    description: "Quentin Did that",
    occurredAt: "2022-11-09T00:00:39.651Z",
    url: "/catalog/",
    status: "ERROR",
  },
];
const DashboardPage = () => {
  const { t } = useTranslation();
  const { data } = useDashboardPageQuery();

  return (
    <Page title={t("Dashboard")}>
      <PageContent>
        <Breadcrumbs className="my-8 px-2">
          <Breadcrumbs.Part href="/pipelines">
            {t("Dashboard")}
          </Breadcrumbs.Part>
        </Breadcrumbs>
        <div className="my-12">
          <div className="flex items-center justify-between">
            <h3 className="ml-2 mt-2 text-lg leading-6 text-gray-900">
              {t("Overview")}
            </h3>
          </div>
          <div className="mt-4">
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
              <Block>
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <BookmarkSquareIcon className="text-cool-gray-400 h-6 w-6" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <DescriptionList
                        displayMode={DescriptionListDisplayMode.LABEL_ABOVE}
                      >
                        <DescriptionList.Item
                          label={
                            <div className="text-cool-gray-500 truncate text-sm font-medium leading-5">
                              {t("Datasources")}
                            </div>
                          }
                        >
                          <div className="text-cool-gray-900 text-lg font-medium leading-7">
                            {data?.catalog.totalItems}
                          </div>
                        </DescriptionList.Item>
                      </DescriptionList>
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
                      <DescriptionList
                        displayMode={DescriptionListDisplayMode.LABEL_ABOVE}
                      >
                        <DescriptionList.Item
                          label={
                            <div className="text-cool-gray-500 truncate text-sm font-medium leading-5">
                              {t("Notebooks")}
                            </div>
                          }
                        >
                          <div className="text-cool-gray-900 text-lg font-medium leading-7">
                            {data?.totalNotebooks}
                          </div>
                        </DescriptionList.Item>
                      </DescriptionList>
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
                      <BookmarkSquareIcon className="text-cool-gray-400 h-6 w-6" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <DescriptionList
                        displayMode={DescriptionListDisplayMode.LABEL_ABOVE}
                      >
                        <DescriptionList.Item
                          label={
                            <div className="text-cool-gray-500 truncate text-sm font-medium leading-5">
                              {t("Pipelines")}
                            </div>
                          }
                        >
                          <div className="text-cool-gray-900 text-lg font-medium leading-7">
                            {data?.dags.totalItems}
                          </div>
                        </DescriptionList.Item>
                      </DescriptionList>
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
            <div className="flex items-center justify-between">
              <h3 className="ml-2 mt-2 text-lg leading-6 text-gray-900">
                {t("Last Activity")}
              </h3>
            </div>
            <div className="mt-4">
              <Block>
                <DataGrid data={data?.lastActivities || []}>
                  <BaseColumn id="name" label={t("Name")}>
                    {(item) => (
                      <div
                        className="truncate text-sm text-gray-900"
                        title={item.description}
                      >
                        {item.description}
                      </div>
                    )}
                  </BaseColumn>
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
                      pathname: value || "",
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
