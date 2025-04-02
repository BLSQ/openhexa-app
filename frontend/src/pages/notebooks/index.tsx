import Button from "core/components/Button";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import BackLayoutHeader from "core/layouts/back/BackLayoutHeader";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import {
  NotebooksPageDocument,
  useNotebooksPageQuery,
} from "notebooks/graphql/queries.generated";

const NotebooksPage = () => {
  const { data } = useNotebooksPageQuery();
  const { t } = useTranslation();
  const router = useRouter();
  if (!data) {
    return null;
  }

  const handleBack = () => {
    if (window.history.length > 1) {
      return router.back();
    } else {
      return router.push("/workspaces");
    }
  };

  return (
    <Page title={t("Notebooks")}>
      <div className="w-screen min-h-screen flex flex-col">
        <BackLayoutHeader
          onBack={handleBack}
          title={
            <div className="flex gap-2">
              <Button
                variant="white"
                onClick={() => router.push("/pipelines")}
                size="sm"
              >
                {t("Airflow Pipelines")}
              </Button>
              <Button onClick={() => router.push("/notebooks")} size="sm">
                {t("Notebooks")}
              </Button>
            </div>
          }
        />
        <iframe className="w-full flex-1" src={data.notebooksUrl}></iframe>
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
