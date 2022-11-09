import Breadcrumbs from "core/components/Breadcrumbs";
import DataCard from "core/components/DataCard";
import CountryProperty from "core/components/DataCard/CountryProperty";
import RenderProperty from "core/components/DataCard/RenderProperty";
import { OnSaveFn } from "core/components/DataCard/Section";
import TagProperty from "core/components/DataCard/TagProperty";
import TextProperty from "core/components/DataCard/TextProperty";
import UserProperty from "core/components/DataCard/UserProperty";
import Page from "core/components/Layout/Page";
import { PageContent } from "core/components/Layout/PageContent";
import { ensureArray } from "core/helpers/array";
import { createGetServerSideProps } from "core/helpers/page";
import { useTranslation } from "next-i18next";
import VisualizationPicture from "visualizations/features/VisualizationPicture";
import { useUpdateExternalDashboardMutation } from "visualizations/graphql/mutations.generated";
import {
  useVisualizationQuery,
  VisualizationDocument,
  VisualizationQuery,
} from "visualizations/graphql/queries.generated";

type Props = {
  visualizationId: string;
};

const VisualizationPage = ({ visualizationId }: Props) => {
  const { t } = useTranslation();

  const { data, refetch } = useVisualizationQuery({
    variables: { id: visualizationId },
  });

  const [mutate] = useUpdateExternalDashboardMutation();

  const onSectionSave: OnSaveFn = async (values) => {
    await mutate({
      variables: {
        input: {
          id: externalDashboard.id,
          name: values.name ?? externalDashboard.name,
          description:
            values.description ?? externalDashboard.description ?? "",
          countries: ensureArray(
            values.countries || externalDashboard.countries
          ).map(({ code }) => ({
            code,
          })),
        },
      },
    });
    await refetch();
  };

  if (!data?.externalDashboard) {
    return null;
  }

  const { externalDashboard } = data;

  return (
    <Page title={externalDashboard.name}>
      <PageContent>
        <Breadcrumbs className="my-8 px-2">
          <Breadcrumbs.Part href="/visualizations">
            {t("Visualizations")}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            href={{
              pathname: "/visualizations/[visualizationId]",
              query: { visualizationId: externalDashboard.id },
            }}
          >
            {externalDashboard.name}
          </Breadcrumbs.Part>
        </Breadcrumbs>
        <div className="space-y-10">
          <DataCard item={externalDashboard}>
            <DataCard.Heading<typeof externalDashboard>>
              {(item) => (
                <div>
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
                        <span>{t("External Dashboard")}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </DataCard.Heading>
            <DataCard.Section title={t("Information")}>
              <RenderProperty id="url" label={t("Url")}>
                {() => (
                  <a
                    href={externalDashboard.url}
                    className="flex items-center text-blue-600 hover:text-blue-500 focus:outline-none"
                  >
                    {externalDashboard.url}
                  </a>
                )}
              </RenderProperty>
            </DataCard.Section>
            <DataCard.Section
              title={t("OpenHexa Metadata")}
              onSave={onSectionSave}
            >
              <TextProperty
                required
                id="name"
                accessor="name"
                label={t("Label")}
                defaultValue="-"
              />
              <TextProperty
                id="description"
                accessor="description"
                label={t("Description")}
                defaultValue="-"
                markdown
              />
              <UserProperty id="owner" accessor="owner" label={t("Owner")} />
              <TagProperty
                id="tags"
                accessor="tags"
                label={t("Tags")}
                defaultValue="-"
              />
              <CountryProperty
                id="countries"
                accessor="countries"
                multiple
                label={t("Location")}
                defaultValue="-"
              />
            </DataCard.Section>
          </DataCard>
        </div>
      </PageContent>
    </Page>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    const { data } = await client.query<VisualizationQuery>({
      query: VisualizationDocument,
      variables: {
        id: ctx.params?.visualizationId,
      },
    });

    if (!data.externalDashboard) {
      return {
        notFound: true,
      };
    }

    return {
      props: {
        visualizationId: ctx.params?.visualizationId,
      },
    };
  },
});

export default VisualizationPage;
