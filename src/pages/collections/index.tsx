import { PlusIcon } from "@heroicons/react/24/outline";
import {
  CollectionsPageDocument,
  useCollectionsPageQuery,
} from "collections/graphql/queries.generated";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import DataGrid from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import CountryColumn from "core/components/DataGrid/CountryColumn";
import DateColumn from "core/components/DataGrid/DateColumn";
import TagColumn from "core/components/DataGrid/TagColumn";
import CreateCollectionDialog from "collections/features/CreateCollectionDialog";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import { PageContent } from "core/components/Layout/PageContent";
import { createGetServerSideProps } from "core/helpers/page";
import Toggle from "core/helpers/Toggle";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { DateTime } from "luxon";
import Page from "core/components/Layout/Page";

type Props = {
  page: number;
  perPage: number;
};

// Refresh list on deletion

const CollectionsPage = (props: Props) => {
  const { t } = useTranslation();
  const { data } = useCollectionsPageQuery({
    variables: {
      page: props.page,
      perPage: props.perPage,
    },
  });
  const router = useRouter();

  const onChangePage = ({ page }: { page: number }) => {
    router.push({ pathname: router.pathname, query: { page } });
  };

  if (!data) {
    return null;
  }

  return (
    <Page title={t("Collections")}>
      <PageContent>
        <Breadcrumbs className="my-8 px-2">
          <Breadcrumbs.Part href="/collections">
            {t("Collections")}
          </Breadcrumbs.Part>
        </Breadcrumbs>
        <div className="space-y-4">
          <div className="flex justify-end">
            <Toggle>
              {({ isToggled, toggle }) => (
                <>
                  <Button onClick={toggle}>
                    <PlusIcon className="mr-1 h-4" />
                    {t("Create")}
                  </Button>
                  <CreateCollectionDialog open={isToggled} onClose={toggle} />
                </>
              )}
            </Toggle>
          </div>
          <Block>
            <DataGrid
              defaultPageSize={15}
              data={data.collections.items}
              totalItems={data.collections.totalItems}
              totalPages={data.collections.totalPages}
              fetchData={onChangePage}
            >
              <TextColumn
                id="name"
                label={t("Name")}
                textPath="name"
                textClassName="text-gray-700 font-medium"
                subtextPath="summary"
                url={(value: any) => ({
                  pathname: "/collections/[collectionId]",
                  query: { collectionId: value.id },
                })}
                minWidth={240}
              />
              <CountryColumn
                max={2}
                defaultValue="-"
                label={t("Locations")}
                accessor="countries"
              />
              <TagColumn
                max={2}
                defaultValue="-"
                label={t("Tags")}
                accessor="tags"
              />
              <DateColumn
                label={t("Created")}
                format={DateTime.DATE_MED}
                accessor="createdAt"
              />
              <TextColumn
                defaultValue="-"
                accessor="author.displayName"
                label={t("Author")}
              />
              <ChevronLinkColumn
                maxWidth="100"
                accessor="id"
                url={(value: any) => ({
                  pathname: "/collections/[collectionId]",
                  query: { collectionId: value },
                })}
              />
            </DataGrid>
          </Block>
        </div>
      </PageContent>
    </Page>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  getServerSideProps: async (ctx, client) => {
    const page = (ctx.query.page as string)
      ? parseInt(ctx.query.page as string, 10)
      : 1;
    const perPage = 15;
    await client.query({
      query: CollectionsPageDocument,
      variables: {
        page,
        perPage,
      },
    });
    return { props: { page, perPage } };
  },
});

export default CollectionsPage;
