import { ChevronRightIcon } from "@heroicons/react/solid";
import Block from "components/Block";
import Breadcrumbs from "components/Breadcrumbs";
import { PageContent } from "components/Layout/PageContent";
import Pagination from "components/Pagination";
import { TableClasses } from "components/Table";
import { FAKE_COLLECTIONS } from "libs/collections";
import { createGetServerSideProps } from "libs/page";
import { useTranslation } from "next-i18next";
import Link from "next/link";

const CollectionsPage = () => {
  const { t } = useTranslation();
  return (
    <PageContent>
      <Breadcrumbs className="my-8 px-2">
        <Breadcrumbs.Part href="/collections">
          {t("Collections")}
        </Breadcrumbs.Part>
      </Breadcrumbs>
      <Block className="mt-12">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className={TableClasses.th}>
                {t("Name")}
              </th>
              <th scope="col" className={TableClasses.th}>
                {t("Location")}
              </th>
              <th scope="col" className={TableClasses.th}>
                {t("Visibility")}
              </th>
              <th scope="col" className={TableClasses.th}>
                {t("Created")}
              </th>
              <th scope="col" className={TableClasses.th}>
                <span className="sr-only">{t("Actions")}</span>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {FAKE_COLLECTIONS.map((collection) => (
              <tr key={collection.id}>
                <td className={TableClasses.td}>
                  <Link
                    href={{
                      pathname: "/collections/[collectionId]",
                      query: { collectionId: collection.id },
                    }}
                  >
                    <a className="text-gray-900">{collection.name}</a>
                  </Link>
                </td>
                <td className={TableClasses.td}>
                  <div className="w-fit rounded-xl border">
                    <div className="flex items-center gap-2 px-2.5 py-1">
                      <img
                        alt="Country flag"
                        className="h-3"
                        src={`/static/flags/${collection.locationCode}.gif`}
                      />
                      {collection.location}
                    </div>
                  </div>
                </td>
                <td className={TableClasses.td}>{collection.visibility}</td>
                <td className={TableClasses.td}>{collection.createdAt}</td>
                <td className={TableClasses.td}>
                  <div className="flex justify-end">
                    <Link
                      href={{
                        pathname: "/collections/[collectionId]",
                        query: { collectionId: collection.id },
                      }}
                    >
                      <a className="inline-flex items-center font-medium text-blue-600 hover:text-blue-900">
                        {t("View")} <ChevronRightIcon className="ml-1 h-4" />
                      </a>
                    </Link>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <Pagination
          className="border-t border-gray-200 px-6 text-gray-500"
          countItems={FAKE_COLLECTIONS.length}
          totalItems={FAKE_COLLECTIONS.length}
          page={1}
          perPage={10}
          totalPages={1}
          onChange={() => {}}
        />
      </Block>
    </PageContent>
  );
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
});

export default CollectionsPage;
