import ManageCollectionItemDialog from "collections/features/ManageCollectionItemDialog";
import Block from "core/components/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import { PageContent } from "core/components/Layout/PageContent";
import { createGetServerSideProps } from "core/helpers/page";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";

const AddToCollectionsPage = () => {
  const { t } = useTranslation();
  const router = useRouter();

  const element = {
    __typename: router.query.type as string,
    id: router.query.id as string,
  };

  const onClose = () => {
    router.push((router.query.redirect as string) || "/");
  };

  return (
    <PageContent>
      <Breadcrumbs className="my-8 px-2">
        <Breadcrumbs.Part href="/collections">
          {t("Collections")}
        </Breadcrumbs.Part>
      </Breadcrumbs>
      <div className="space-y-4">
        <Block className="h-96">
          <ManageCollectionItemDialog
            element={element}
            open
            onClose={onClose}
          />
        </Block>
      </div>
    </PageContent>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
});

export default AddToCollectionsPage;
