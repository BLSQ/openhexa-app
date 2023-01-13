import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useNotebooksPageQuery } from "notebooks/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

const WorkspaceNotebooksPage: NextPageWithLayout = () => {
  const { t } = useTranslation();
  const { data } = useNotebooksPageQuery();

  if (!data) {
    return null;
  }

  return (
    <Page title={t("Workspace")}>
      <iframe className="h-full w-full flex-1" src={data.notebooksUrl}></iframe>
    </Page>
  );
};

WorkspaceNotebooksPage.getLayout = (page, pageProps) => {
  return (
    <WorkspaceLayout mainClassName="min-h-screen" pageProps={pageProps}>
      {page}
    </WorkspaceLayout>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
});

export default WorkspaceNotebooksPage;
