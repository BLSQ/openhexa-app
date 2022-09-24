import { gql, useMutation } from "@apollo/client";
import {
  ClockIcon,
  ExternalLinkIcon,
  PlayIcon,
} from "@heroicons/react/outline";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import DataCard from "core/components/DataCard";
import CountryProperty from "core/components/DataCard/CountryProperty";
import TagProperty from "core/components/DataCard/TagProperty";
import TextProperty from "core/components/DataCard/TextProperty";
import UserProperty from "core/components/DataCard/UserProperty";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import DateColumn from "core/components/DataGrid/DateColumn";
import UserColumn from "core/components/DataGrid/UserColumn";
import Page from "core/components/Layout/Page";
import { PageContent } from "core/components/Layout/PageContent";
import Link from "core/components/Link";
import { createGetServerSideProps } from "core/helpers/page";
import { formatDuration } from "core/helpers/time";
import { Country, DagRunTrigger } from "graphql-types";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import { PipelineRunStatusBadge_DagRunFragment } from "pipelines/features/PipelineRunStatusBadge.generated";
import { useUpdatePipelineMutation } from "pipelines/graphql/mutations.generated";
import {
  PipelinePageDocument,
  PipelinePageQuery,
  usePipelinePageQuery,
} from "pipelines/graphql/queries.generated";

type Props = {
  page: number;
  perPage: number;
};

const PipelinePage = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();

  const { data, refetch } = usePipelinePageQuery({
    variables: { id: router.query.pipelineId as string },
  });

  const [updatePipeline] = useUpdatePipelineMutation();

  const onChangePage = ({ page }: { page: number }) => {
    refetch({
      page,
      perPage: 10,
      id: router.query.pipelineId as string,
    });
  };

  const onSave = async (values: any) => {
    await updatePipeline({
      variables: {
        input: {
          id: dag.id,
          label: values.label,
          schedule: values.schedule,
          description: values.description,
          countries: values.countries?.map((c: Country) => ({ code: c.code })),
        },
      },
    });
    await refetch();
  };

  if (!data || !data.dag) {
    return null;
  }

  const { dag } = data;

  return (
    <Page title={t("Pipelines")}>
      <PageContent>
        <Breadcrumbs className="my-8 px-2">
          <Breadcrumbs.Part href="/pipelines">
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
        </Breadcrumbs>
        <div className="space-y-12">
          <DataCard item={dag}>
            <DataCard.Heading<typeof dag>
              titleAccessor={(item) => item.label || item.externalId}
              subtitleAccessor={(item) => (item.label ? item.externalId : null)}
              renderActions={(item) => (
                <div className="flex items-center gap-2">
                  <Link href={item.externalUrl}>
                    <Button
                      variant="white"
                      size="sm"
                      leadingIcon={<ExternalLinkIcon className="w-6" />}
                    >
                      {t("Open in Airflow")}
                    </Button>
                  </Link>
                  <Link
                    href={{
                      pathname: "/pipelines/[pipelineId]/run",
                      query: { pipelineId: item.id },
                    }}
                  >
                    <Button
                      size="sm"
                      leadingIcon={<PlayIcon className="w-6" />}
                    >
                      {t("Configure & run")}
                    </Button>
                  </Link>
                </div>
              )}
            />
            <DataCard.Section title={t("Pipeline Metadata")} onSave={onSave}>
              <TextProperty
                id="label"
                accessor="label"
                label={t("Label")}
                defaultValue="-"
              />
              <CountryProperty
                id="countries"
                accessor="countries"
                multiple
                label={t("Location")}
                defaultValue="-"
              />
              <TextProperty
                id="description"
                accessor={"description"}
                label={t("Description")}
                defaultValue="-"
                markdown
              />
            </DataCard.Section>
            <DataCard.Section
              title={t("Airflow Data")}
              onSave={onSave}
              defaultOpen={false}
            >
              <TextProperty
                readonly
                id="externalId"
                accessor="externalId"
                label={t("Identifier")}
                defaultValue="-"
              />
              <TextProperty
                id="schedule"
                accessor="schedule"
                label={t("Schedule")}
                defaultValue="-"
              />
              <UserProperty id="user" accessor="user" label={t("Report to")} />
              <TextProperty
                readonly
                id="description"
                accessor="template.description"
                label={t("Template Description")}
                markdown
              />
            </DataCard.Section>
          </DataCard>
          <div>
            <h3 className="mb-4 text-lg font-medium">{t("Runs")}</h3>
            <Block>
              <DataGrid
                defaultPageSize={10}
                data={dag.runs.items}
                totalItems={dag.runs.totalItems}
                totalPages={dag.runs.totalPages}
                fetchData={onChangePage}
              >
                <BaseColumn id="id" label={t("Trigger")}>
                  {(item) => (
                    <Link
                      linkStyle="text-gray-700 hover:text-gray-600"
                      href={{
                        pathname: "/pipelines/[pipelinesId]/runs/[runId]",
                        query: { pipelinesId: dag.id, runId: item.id },
                      }}
                    >
                      {item.triggerMode === DagRunTrigger.Manual ? (
                        <div className="flex items-center gap-2">
                          <PlayIcon className="w-6" />
                          <span>{t("Manual")}</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <ClockIcon className="w-6" />
                          <span>{t("Scheduled")}</span>
                        </div>
                      )}
                    </Link>
                  )}
                </BaseColumn>
                <DateColumn
                  label={t("Executed on")}
                  format={DateTime.DATETIME_SHORT}
                  accessor="executionDate"
                />
                <BaseColumn<PipelineRunStatusBadge_DagRunFragment>
                  label={t("Status")}
                  id="status"
                >
                  {(item) => <PipelineRunStatusBadge dagRun={item} />}
                </BaseColumn>
                <BaseColumn label={t("Duration")} accessor="duration">
                  {(value) => (
                    <span>{value ? formatDuration(value) : "-"}</span>
                  )}
                </BaseColumn>
                <UserColumn label={t("User")} accessor="user" />
                <ChevronLinkColumn
                  maxWidth="100"
                  accessor="id"
                  url={(value: any) => ({
                    pathname: "/pipelines/[pipelinesId]/runs/[runId]",
                    query: { pipelinesId: dag.id, runId: value },
                  })}
                />
              </DataGrid>
            </Block>
          </div>
        </div>
      </PageContent>
    </Page>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  getServerSideProps: async (ctx, client) => {
    const { data } = await client.query<PipelinePageQuery>({
      query: PipelinePageDocument,
      variables: {
        id: ctx.params?.pipelineId as string,
      },
    });

    if (!data.dag) {
      return {
        notFound: true,
      };
    }
  },
});

export default PipelinePage;
