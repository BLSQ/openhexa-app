import {
  ArrowTopRightOnSquareIcon,
  ClockIcon,
  PlayCircleIcon,
  PlayIcon,
} from "@heroicons/react/24/outline";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import DataCard from "core/components/DataCard";
import CountryProperty from "core/components/DataCard/CountryProperty";
import TextProperty from "core/components/DataCard/TextProperty";
import UserProperty from "core/components/DataCard/UserProperty";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import DateColumn from "core/components/DataGrid/DateColumn";
import UserColumn from "core/components/DataGrid/UserColumn";
import Page from "core/components/Page";
import DefaultLayout from "core/layouts/default";
import Link from "core/components/Link";
import { createGetServerSideProps } from "core/helpers/page";
import { formatDuration } from "core/helpers/time";
import { Country, DagRunTrigger } from "graphql-types";
import useMe from "identity/hooks/useMe";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import PipelineRunFavoriteTrigger from "pipelines/features/PipelineRunFavoriteTrigger";
import { PipelineRunFavoriteTrigger_RunFragment } from "pipelines/features/PipelineRunFavoriteTrigger/PipelineRunFavoriteTrigger.generated";
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
  const me = useMe();

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
      <DefaultLayout.PageContent>
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
              renderActions={(item) => (
                <div className="flex items-center gap-2">
                  {me?.permissions.superUser && (
                    <a target="_blank" rel="noreferrer" href={item.externalUrl}>
                      <Button
                        variant="outlined"
                        size="sm"
                        leadingIcon={
                          <ArrowTopRightOnSquareIcon className="w-6" />
                        }
                      >
                        {t("Open in Airflow")}
                      </Button>
                    </a>
                  )}
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
            <DataCard.FormSection
              title={t("Pipeline Metadata")}
              onSave={onSave}
            >
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
            </DataCard.FormSection>
            <DataCard.FormSection
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
            </DataCard.FormSection>
          </DataCard>
          <div>
            <h3 className="mb-4 text-lg font-medium">{t("Runs")}</h3>
            <Block>
              <DataGrid
                defaultPageSize={10}
                data={dag.runs.items}
                totalItems={dag.runs.totalItems}
                fetchData={onChangePage}
              >
                <BaseColumn<PipelineRunFavoriteTrigger_RunFragment>
                  id="favorite"
                  label=""
                  width={50}
                  className="pr-0"
                >
                  {(item) => <PipelineRunFavoriteTrigger run={item} />}
                </BaseColumn>
                <BaseColumn id="id" label={t("Run")}>
                  {(item) => (
                    <Link
                      customStyle="text-gray-700 hover:text-gray-600"
                      href={{
                        pathname: "/pipelines/[pipelinesId]/runs/[runId]",
                        query: { pipelinesId: dag.id, runId: item.id },
                      }}
                    >
                      <div className="flex items-center gap-2">
                        {item.triggerMode === DagRunTrigger.Manual && (
                          <PlayCircleIcon className="w-6" />
                        )}
                        {item.triggerMode === DagRunTrigger.Scheduled && (
                          <ClockIcon className="w-6" />
                        )}
                        {item.label ? item.label : null}

                        {!item.label &&
                          item.triggerMode === DagRunTrigger.Manual && (
                            <span>{t("Manual")}</span>
                          )}
                        {!item.label &&
                          item.triggerMode === DagRunTrigger.Scheduled && (
                            <div className="flex items-center gap-2">
                              <span>{t("Scheduled")}</span>
                            </div>
                          )}
                      </div>
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
      </DefaultLayout.PageContent>
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
