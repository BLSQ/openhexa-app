import Page from "core/components/Layout/Page";
import { PageContent } from "core/components/Layout/PageContent";
import { createGetServerSideProps } from "core/helpers/page";
import { useTranslation } from "next-i18next";
import {
  NotebooksPageDocument,
  useNotebooksPageQuery,
} from "notebooks/graphql/queries.generated";

const NotebooksPage = () => {
  const { data } = useNotebooksPageQuery();
  const { t } = useTranslation();
  if (!data) {
    return null;
  }

  return (
    <Page title={t("Notebooks")}>
      <div className="flex flex-1 flex-col">
        <iframe className="flex-1" src={data.notebooksUrl}></iframe>
      </div>
    </Page>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  getServerSideProps: async (ctx, client) => {
    await client.query({
      query: NotebooksPageDocument,
    });
  },
});

export default NotebooksPage;
