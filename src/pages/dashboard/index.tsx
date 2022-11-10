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
                      <BookmarkSquareIcon className="h-6 w-6" />
                    </div>
                    <dl className="ml-5 w-0 flex-1">
                      <dt>
                        <div className="text-sm font-medium">
                          {t("Datasources")}
                        </div>
                      </dt>
                      <dd>
                        <div className="text-lg font-medium">
                          {data?.catalog.totalItems}
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
                <div className="px-5 py-3">
                  <div className="text-sm">
                    <Link
                      href="/catalog"
                      className="font-medium text-blue-600 hover:text-blue-900"
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
                      <BookOpenIcon className="h-6 w-6" />
                    </div>
                    <dl className="ml-5 w-0 flex-1">
                      <dt className="text-sm font-medium">{t("Notebooks")}</dt>
                      <dd className="text-lg font-medium">
                        {data?.totalNotebooks}
                      </dd>
                    </dl>
                  </div>
                </div>
                <div className="px-5 py-3">
                  <div className="text-sm">
                    <Link
                      href="/notebooks"
                      className="font-medium text-blue-600 hover:text-blue-900"
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
                      <BeakerIcon className="h-6 w-6" />
                    </div>
                    <dl className="ml-5 w-0 flex-1">
                      <dt>
                        <div className="truncate text-sm font-medium">
                          {t("Pipelines")}
                        </div>
                      </dt>
                      <dd>
                        <div className="text-lg font-medium ">
                          {data?.dags.totalItems}
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
                <div className=" px-5 py-3">
                  <div className="text-sm">
                    <Link
                      href="/pipelines"
                      className="font-medium text-blue-600 hover:text-blue-900"
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
                    accessor={(value) => (
                      <div
                        dangerouslySetInnerHTML={{ __html: value.description }}
                      />
                    )}
                    className="... truncate"
                    minWidth={250}
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
