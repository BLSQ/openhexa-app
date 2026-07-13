import { PlusIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import {
  useWorkspaceDataStudioPageQuery,
  WorkspaceDataStudioPageDocument,
} from "workspaces/graphql/queries.generated";
import DataStudioLayout from "workspaces/layouts/DataStudioLayout";

type Props = {
  workspaceSlug: string;
};

const WorkspaceSavedQueriesPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const { data } = useWorkspaceDataStudioPageQuery({
    variables: { workspaceSlug: props.workspaceSlug },
  });

  if (!data?.workspace) {
    return null;
  }
  const { workspace } = data;
  const basePath = `/workspaces/${encodeURIComponent(workspace.slug)}/data-studio`;

  return (
    <Page title={t("Saved queries")}>
      <DataStudioLayout workspace={workspace} currentTab="saved">
        <div className="h-full overflow-auto bg-gray-50">
          <div className="mx-auto max-w-[1180px] px-8 pt-7 pb-5">
            <div className="mb-5 flex items-center justify-between">
              <h1 className="text-[22px] font-semibold tracking-tight text-gray-900">
                {t("Saved queries")}
              </h1>
              <Button
                leadingIcon={<PlusIcon className="h-4 w-4" />}
                onClick={() => router.push(basePath)}
              >
                {t("New query")}
              </Button>
            </div>
            {/* Populated in a later step: search + DataGrid of saved queries. */}
            <div className="rounded-md border border-gray-200 bg-white p-10 text-center text-sm text-gray-500 shadow-xs">
              {t("The saved queries list will appear here.")}
            </div>
          </div>
        </div>
      </DataStudioLayout>
    </Page>
  );
};

WorkspaceSavedQueriesPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await DataStudioLayout.prefetch(ctx, client);
    const { data } = await client.query({
      query: WorkspaceDataStudioPageDocument,
      variables: {
        workspaceSlug: ctx.params?.workspaceSlug,
      },
    });

    if (!data.workspace) {
      return {
        notFound: true,
      };
    }
    return {
      props: { workspaceSlug: data.workspace.slug },
    };
  },
});

export default WorkspaceSavedQueriesPage;
