import { TrashIcon } from "@heroicons/react/24/outline";
import Badge from "core/components/Badge";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import DataCard from "core/components/DataCard";
import DateProperty from "core/components/DataCard/DateProperty";
import { OnSaveFn } from "core/components/DataCard/FormSection";
import TextProperty from "core/components/DataCard/TextProperty";
import DescriptionList from "core/components/DescriptionList";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import useCacheKey from "core/hooks/useCacheKey";
import { useTranslation } from "next-i18next";
import ConnectionFieldsSection from "workspaces/features/ConnectionFieldsSection";
import ConnectionUsageSnippets from "workspaces/features/ConnectionUsageSnippets";
import DeleteConnectionTrigger from "workspaces/features/DeleteConnectionTrigger";
import { useUpdateConnectionMutation } from "workspaces/graphql/mutations.generated";
import {
  ConnectionPageDocument,
  ConnectionPageQuery,
  ConnectionPageQueryVariables,
  useConnectionPageQuery,
} from "workspaces/graphql/queries.generated";
import { CONNECTION_TYPES } from "workspaces/helpers/connection";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  workspaceSlug: string;
  connectionId: string;
};

const WorkspaceConnectionPage: NextPageWithLayout = ({
  workspaceSlug,
  connectionId,
}: Props) => {
  const { t } = useTranslation();

  const { data, refetch } = useConnectionPageQuery({
    variables: { workspaceSlug, connectionId },
  });

  useCacheKey(["connections", data?.connection?.id], () => refetch());

  const [updateConnection] = useUpdateConnectionMutation();

  const onSave: OnSaveFn = async (values, item) => {
    await updateConnection({
      variables: {
        input: {
          id: item.id,
          name: values.name,
          slug: values.slug,
          description: values.description,
        },
      },
    });
  };

  if (!data?.workspace || !data?.connection) {
    return null;
  }
  const { workspace, connection } = data;

  const type = CONNECTION_TYPES[connection.type];
  if (!connection || !type) {
    return null;
  }

  return (
    <Page title={connection.name}>
      <WorkspaceLayout workspace={workspace}>
        <WorkspaceLayout.Header className="flex items-center justify-between">
          <Breadcrumbs withHome={false}>
            <Breadcrumbs.Part
              isFirst
              href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
            >
              {workspace.name}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              href={`/workspaces/${encodeURIComponent(
                workspace.slug
              )}/connections`}
            >
              {t("Connections")}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              isLast
              href={`/workspaces/${encodeURIComponent(
                workspace.slug
              )}/pipelines/${encodeURIComponent(connection.id)}`}
            >
              {connection.name}
            </Breadcrumbs.Part>
          </Breadcrumbs>
          <DeleteConnectionTrigger
            workspace={workspace}
            connection={connection}
          >
            {({ onClick }) => (
              <Button
                className="bg-red-500 hover:bg-red-700 focus:ring-red-500"
                onClick={onClick}
                leadingIcon={<TrashIcon className="w-4" />}
              >
                {t("Delete")}
              </Button>
            )}
          </DeleteConnectionTrigger>
        </WorkspaceLayout.Header>
        <WorkspaceLayout.PageContent>
          <DataCard item={connection} className="divide-y-2 divide-gray-100">
            <div>
              <DataCard.FormSection
                onSave={onSave}
                title={t("Information")}
                className="space-y-4"
              >
                <TextProperty id="name" label={t("Name")} accessor="name" />
                <TextProperty
                  id="slug"
                  label={t("Slug")}
                  accessor="slug"
                  help={t(
                    "The slug is used as the prefix for the environment variables in the notebooks"
                  )}
                  className="font-mono uppercase"
                />
                <DescriptionList.Item label={t("Type")}>
                  <Badge className={type.color}>{type.label ?? "custom"}</Badge>
                </DescriptionList.Item>
                <DateProperty
                  readonly
                  id="createdAt"
                  accessor="createdAt"
                  label={t("Created at")}
                />
                <TextProperty
                  id="description"
                  label={t("Description")}
                  accessor="description"
                />
              </DataCard.FormSection>
              {workspace.permissions.update && (
                <ConnectionFieldsSection connection={connection} />
              )}
            </div>
            <DataCard.Section title={t("Usage")}>
              <div className="space-y-2">
                <p>
                  The following guides gives you a general introduction to
                  connections and how you can use them in notebooks or data
                  pipelines:
                </p>
                <ul className="list list-inside list-disc">
                  <li>
                    <a
                      href={
                        "https://github.com/BLSQ/openhexa/wiki/User-manual#adding-and-managing-connections"
                      }
                      className="text-blue-600 hover:text-blue-500 focus:outline-none"
                      target="_blank"
                    >
                      {t("Connections general documentation")}
                    </a>
                  </li>
                  <li>
                    <a
                      href={
                        "https://github.com/BLSQ/openhexa/wiki/Using-notebooks-in-OpenHexa#using-connections"
                      }
                      className="text-blue-600 hover:text-blue-500 focus:outline-none"
                      target="_blank"
                    >
                      {t("Using connections in notebooks")}
                    </a>
                  </li>
                  <li>
                    <a
                      href={
                        "https://github.com/BLSQ/openhexa/wiki/Writing-OpenHexa-pipelines#using-connections"
                      }
                      className="text-blue-600 hover:text-blue-500 focus:outline-none"
                      target="_blank"
                    >
                      {t("Using connections in pipelines")}
                    </a>
                  </li>
                </ul>
              </div>
            </DataCard.Section>
          </DataCard>
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
    </Page>
  );
};

WorkspaceConnectionPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WorkspaceLayout.prefetch(ctx, client);
    const workspaceSlug = ctx.params?.workspaceSlug as string;
    const connectionId = ctx.params?.connectionId as string;
    const { data } = await client.query<
      ConnectionPageQuery,
      ConnectionPageQueryVariables
    >({
      query: ConnectionPageDocument,
      variables: { workspaceSlug, connectionId },
    });

    if (!data.workspace || !data.connection) {
      return {
        notFound: true,
      };
    }

    return {
      props: {
        connectionId,
        workspaceSlug,
      },
    };
  },
});

export default WorkspaceConnectionPage;
