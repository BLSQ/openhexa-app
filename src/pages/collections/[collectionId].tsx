import { gql, useMutation } from "@apollo/client";
import CollectionActionsMenu from "collections/features/CollectionActionsMenu";
import CollectionDataSourceViewerDialog from "collections/features/CollectionDataSourceViewerDialog";
import CollectionElementsTable from "collections/features/CollectionElementsTable";
import { useUpdateCollectionMutation } from "collections/graphql/mutations.generated";
import {
  CollectionPageDocument,
  CollectionPageQuery,
  useCollectionPageQuery,
} from "collections/graphql/queries.generated";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import DataCard from "core/components/DataCard";
import CountryProperty from "core/components/DataCard/CountryProperty";
import DateProperty from "core/components/DataCard/DateProperty";
import { OnSaveFn } from "core/components/DataCard/Section";
import TagProperty from "core/components/DataCard/TagProperty";
import TextProperty from "core/components/DataCard/TextProperty";
import UserProperty from "core/components/DataCard/UserProperty";
import { PageContent } from "core/components/Layout/PageContent";
import { ensureArray } from "core/helpers/array";
import { createGetServerSideProps } from "core/helpers/page";
import useToggle from "core/hooks/useToggle";
import { useTranslation } from "next-i18next";

type Props = {
  collectionId: string;
};

const CollectionPage = ({ collectionId }: Props) => {
  const { t } = useTranslation();
  const [isDialogOpen, { toggle: toggleDialog }] = useToggle();
  const [isEditingElements, { toggle: toggleEditingElements }] = useToggle();

  const { data, refetch } = useCollectionPageQuery({
    variables: { id: collectionId },
  });

  const [mutate] = useUpdateCollectionMutation();

  if (!data?.collection) {
    return null;
  }

  const onSectionSave: OnSaveFn = async (values) => {
    await mutate({
      variables: {
        input: {
          id: collection.id,
          name: values.name ?? collection.name,
          description: values.description ?? collection.description ?? "",
          summary: values.summary,
          tagIds: (values.tags || collection.tags)?.map(
            (t: { id: string }) => t.id
          ),
          countries: ensureArray(values.countries || collection.countries).map(
            ({ code }) => ({
              code,
            })
          ),
        },
      },
    });
    await refetch();
  };

  const { collection } = data;
  console.log(collection);
  return (
    <>
      <PageContent>
        <Breadcrumbs className="my-8 px-2">
          <Breadcrumbs.Part href="/collections">
            {t("Collections")}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            href={{
              pathname: "/collections/[collectionId]",
              query: { collectionId: collection.id },
            }}
          >
            {collection.name}
          </Breadcrumbs.Part>
        </Breadcrumbs>
        <div className="space-y-10">
          <DataCard item={collection}>
            <DataCard.Heading<typeof collection>
              titleAccessor="name"
              subtitleAccessor="summary"
              renderActions={(item) => (
                <CollectionActionsMenu collection={item} />
              )}
            />
            <DataCard.Section title={t("Properties")} onSave={onSectionSave}>
              <TextProperty
                id="name"
                accessor="name"
                required
                label={t("Name")}
                defaultValue="-"
              />
              <TextProperty
                id="summary"
                accessor="summary"
                label={t("Summary")}
                defaultValue="-"
              />
              <UserProperty
                id="author"
                readonly
                accessor="author"
                label={t("Created By")}
              />
              <DateProperty
                id="createdAt"
                readonly
                accessor="createdAt"
                label={t("Created")}
              />
              <CountryProperty
                id="countries"
                multiple
                accessor="countries"
                label={t("Locations")}
              />
              <TagProperty id="tags" accessor="tags" label={t("Tags")} />
            </DataCard.Section>
            <DataCard.Section title={t("Description")} onSave={onSectionSave}>
              <TextProperty
                required
                id="description"
                accessor="description"
                label={t("Description")}
                markdown
              />
            </DataCard.Section>
          </DataCard>

          <section>
            <div className="mb-4 flex w-full items-center justify-between">
              <h3 className="font-medium">{t("Elements")}</h3>
              {collection.authorizedActions.canUpdate && isEditingElements && (
                <Button
                  onClick={toggleEditingElements}
                  variant="secondary"
                  size="sm"
                >
                  {t("Done")}
                </Button>
              )}
              {collection.authorizedActions.canUpdate && !isEditingElements && (
                <Button
                  onClick={toggleEditingElements}
                  variant="white"
                  size="sm"
                >
                  {t("Edit")}
                </Button>
              )}
            </div>
            <Block>
              <CollectionElementsTable
                isEditing={isEditingElements}
                elements={collection.elements.items}
                collection={collection}
              />
            </Block>
          </section>
        </div>
      </PageContent>

      <CollectionDataSourceViewerDialog
        open={isDialogOpen}
        onClose={toggleDialog}
      />
    </>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    const { data } = await client.query<CollectionPageQuery>({
      query: CollectionPageDocument,
      variables: {
        id: ctx.params?.collectionId,
      },
    });

    if (!data.collection) {
      return {
        notFound: true,
      };
    }

    return {
      props: {
        collectionId: ctx.params?.collectionId,
      },
    };
  },
});

export default CollectionPage;
