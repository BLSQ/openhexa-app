import {
  CheckIcon,
  PencilIcon,
  PlusIcon,
  XIcon,
} from "@heroicons/react/outline";
import CollectionActionsMenu from "collections/features/CollectionActionsMenu";
import CollectionDataSourceViewerDialog from "collections/features/CollectionDataSourceViewerDialog";
import CollectionElementsTable from "collections/features/CollectionElementsTable";
import { useUpdateCollectionMutation } from "collections/graphql/mutations.generated";
import {
  CollectionPageDocument,
  CollectionPageQuery,
  useCollectionPageQuery,
} from "collections/graphql/queries.generated";
import { addToCollection } from "collections/helpers/collections";
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
import Page from "core/components/Layout/Page";
import { PageContent } from "core/components/Layout/PageContent";
import Spinner from "core/components/Spinner";
import { ensureArray } from "core/helpers/array";
import { createGetServerSideProps } from "core/helpers/page";
import useCacheKey from "core/hooks/useCacheKey";
import useToggle from "core/hooks/useToggle";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import Quicksearch from "search/features/Quicksearch";
import { QuickSearchResult } from "search/features/Quicksearch/Quicksearch";

type Props = {
  collectionId: string;
};

const QuickActionAddToCollection = (props: {
  collectionId: string;
  element: QuickSearchResult;
  onSubmit: () => void;
}) => {
  const { element, collectionId, onSubmit } = props;
  const [flag, setFlag] = useState<"done" | "error" | "loading" | "ready">(
    "ready"
  );

  const onClick = async () => {
    setFlag("loading");
    try {
      await addToCollection(collectionId, {
        id: element.object_id,
        app: element.app_label,
        model: element.content_type_model,
      });
      setFlag("done");
      onSubmit();
    } catch {
      setFlag("error");
    }
  };

  return (
    <Button
      onClick={onClick}
      variant="secondary"
      size="sm"
      disabled={flag !== "ready"}
    >
      {flag === "done" && <CheckIcon className="w-4" />}
      {flag === "ready" && <PlusIcon className="w-4" />}
      {flag === "loading" && <Spinner size="xs" />}
      {flag === "error" && <XIcon className="w-4" />}
    </Button>
  );
};

const CollectionPage = ({ collectionId }: Props) => {
  const { t } = useTranslation();
  const [isDialogOpen, { toggle: toggleDialog }] = useToggle();
  const [isSearchOpen, { toggle: toggleSearch }] = useToggle();
  const [isEditingElements, { toggle: toggleEditingElements }] = useToggle();

  const { data, refetch } = useCollectionPageQuery({
    variables: { id: collectionId },
  });

  const [mutate] = useUpdateCollectionMutation();

  useCacheKey("collections", () => refetch());

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

  return (
    <Page title={collection.name}>
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
              <h3 className="flex-1 font-medium">{t("Elements")}</h3>
              <div className="flex items-center gap-2">
                {collection.authorizedActions.canUpdate && (
                  <Button
                    onClick={toggleSearch}
                    variant="secondary"
                    size="sm"
                    leadingIcon={<PlusIcon className="w-3" />}
                  >
                    {t("Add")}
                  </Button>
                )}
                {collection.authorizedActions.canUpdate && !isEditingElements && (
                  <Button
                    onClick={toggleEditingElements}
                    variant="secondary"
                    size="sm"
                    leadingIcon={<PencilIcon className="w-3" />}
                  >
                    {t("Edit")}
                  </Button>
                )}
                {collection.authorizedActions.canUpdate && isEditingElements && (
                  <Button
                    onClick={toggleEditingElements}
                    variant="secondary"
                    size="sm"
                  >
                    {t("Done")}
                  </Button>
                )}
              </div>
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

      <Quicksearch
        renderActions={(element) => (
          <QuickActionAddToCollection
            onSubmit={() => refetch()}
            collectionId={collection.id}
            element={element}
          />
        )}
        open={isSearchOpen}
        onClose={toggleSearch}
      />
    </Page>
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
