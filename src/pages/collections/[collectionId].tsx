import { ExternalLinkIcon, PencilIcon } from "@heroicons/react/outline";
import {
  ChevronRightIcon,
  DocumentDownloadIcon,
} from "@heroicons/react/outline";
import clsx from "clsx";
import ReactMarkdown from "react-markdown";
import Badge from "components/Badge";
import Block from "components/Block";
import Breadcrumbs from "components/Breadcrumbs";
import Button from "components/Button";
import DescriptionList from "components/DescriptionList";
import { PageContent } from "components/Layout/PageContent";
import { TableClasses } from "components/Table";
import Time from "components/Time";
import CollectionDataSourceViewerDialog from "features/collection/CollectionDataSourceViewerDialog";
import useToggle from "hooks/useToggle";
import { FAKE_COLLECTIONS } from "libs/collections";
import { createGetServerSideProps } from "libs/page";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import Comments from "components/Comments";

const CollectionPage = () => {
  const router = useRouter();
  const { t } = useTranslation();

  const [isDialogOpen, { toggle: toggleDialog }] = useToggle();

  const collection = FAKE_COLLECTIONS.find(
    (col) => col.id === (router.query.collectionId as string)
  );

  if (!collection) {
    return null;
  }

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
          <Block as="section" className="mt-12 divide-y divide-gray-200">
            <Block.Title className="">
              <span>{collection.name}</span>
              {collection.excerpt && (
                <div className="mt-2 text-sm text-gray-400">
                  {collection.excerpt}
                </div>
              )}
            </Block.Title>
            <Block.Content>
              <h4 className="mt-1 mb-4 font-medium">
                {t("Collection properties")}
                <button className="ml-4 inline-flex items-center text-sm text-blue-500 hover:text-blue-400">
                  {t("Edit")}
                  <PencilIcon className="ml-1 h-4" />
                </button>
              </h4>
              <DescriptionList>
                <DescriptionList.Item label={t("Name")}>
                  {collection.name}
                </DescriptionList.Item>
                <DescriptionList.Item label={t("Created by")}>
                  {collection.createdBy}
                </DescriptionList.Item>
                <DescriptionList.Item label={t("Created")}>
                  {collection.createdAt}
                </DescriptionList.Item>
                <DescriptionList.Item label={t("Location")}>
                  <Badge
                    className={
                      "cursor-pointer border-gray-300 bg-gray-50 hover:bg-opacity-70"
                    }
                  >
                    <img
                      alt="Country flag"
                      className="mr-1 h-3"
                      src={`/static/flags/${collection.locationCode}.gif`}
                    />
                    {collection.location}
                  </Badge>
                </DescriptionList.Item>
                <DescriptionList.Item label={t("Tags")}>
                  <div className="space-x-2">
                    {collection.tags?.length ? (
                      collection.tags.map((t, i) => (
                        <Badge
                          className={clsx(
                            "cursor-pointer hover:bg-opacity-70",
                            [
                              "border-purple-400 bg-purple-100",
                              "border-amber-400 bg-amber-100",
                              "border-lime-400 bg-lime-100",
                            ][i % 3]
                          )}
                          key={t}
                        >
                          {t}
                        </Badge>
                      ))
                    ) : (
                      <span>-</span>
                    )}
                  </div>
                </DescriptionList.Item>
              </DescriptionList>
            </Block.Content>
            <Block.Content>
              <h4 className="mt-1 mb-4 font-medium">
                {t("Description")}
                <button className="ml-4 inline-flex items-center text-sm text-blue-500 hover:text-blue-400">
                  {t("Edit")}
                  <PencilIcon className="ml-1 h-4" />
                </button>
              </h4>
              <ReactMarkdown className="prose max-w-3xl text-sm ">
                {collection.description}
              </ReactMarkdown>
            </Block.Content>
            <Block.Content>
              <h4 className="mt-1 mb-4 font-medium">{t("Discussion")}</h4>
              <Comments />
            </Block.Content>
          </Block>

          {/* *********** DHIS Sources *********** */}

          <section>
            <h3 className="mb-4 font-bold">{t("DHIS2 Data")}</h3>
            <Block>
              <table className={TableClasses.table}>
                <thead className={TableClasses.thead}>
                  <tr>
                    <th className={TableClasses.th}>{t("Instance")}</th>
                    <th className={TableClasses.th}>{t("Content")}</th>
                    <th className={TableClasses.th}>{t("Last extracted")}</th>
                    <th className={TableClasses.th}>
                      <span className="sr-only">{t("Actions")}</span>
                    </th>
                  </tr>
                </thead>
                <tbody className={TableClasses.tbody}>
                  {[
                    {
                      name: "SNIC RDC",
                      elements: ["103 data elements", "3 indicators"],
                      lastExtractedAt: "10 hours ago",
                    },
                    {
                      name: "DHIS2 BFA",
                      elements: ["5 data elements", "1 indicators"],
                      lastExtractedAt: "10 hours ago",
                    },
                  ].map((row, idx) => (
                    <tr key={idx}>
                      <td className={TableClasses.td}>
                        <span className="text-gray-900">{row.name}</span>
                      </td>
                      <td className={TableClasses.td}>
                        {row.elements.join(", ") || "-"}
                      </td>
                      <td className={TableClasses.td}>{row.lastExtractedAt}</td>
                      <td className={TableClasses.td}>
                        <div className="flex items-center justify-end gap-6">
                          <Button
                            size="sm"
                            variant="white"
                            leadingIcon={
                              <DocumentDownloadIcon className="h-4" />
                            }
                          >
                            {t("Extract")}
                          </Button>
                          <button
                            onClick={toggleDialog}
                            className="inline-flex items-center font-medium text-blue-600 hover:text-blue-900"
                          >
                            {t("Details")}
                            <ChevronRightIcon className="ml-1 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Block>
          </section>

          {/* *********** S3 *********** */}

          <section>
            <h3 className="mb-4 font-bold">{t("S3 Data")}</h3>
            <Block>
              <table className={TableClasses.table}>
                <thead className={TableClasses.thead}>
                  <tr>
                    <th className={TableClasses.th}>{t("Filename")}</th>
                    <th className={TableClasses.th}>{t("Type")}</th>
                    <th className={TableClasses.th}>{t("Size")}</th>
                    <th className={TableClasses.th}>{t("Created")}</th>
                    <th className={TableClasses.th}>
                      <span className="sr-only">{t("Actions")}</span>
                    </th>
                  </tr>
                </thead>
                <tbody className={TableClasses.tbody}>
                  {[
                    {
                      name: "covid_tracker.csv",
                      type: "CSV",
                      size: "755KB",
                      createdAt: "2022-04-01T11:32:12",
                    },
                    {
                      name: "contours.gpkg",
                      type: "Geopackage",
                      size: "17MB",
                      createdAt: "2022-04-04T09:32:11",
                    },
                    {
                      name: "malaria_vaccines.xls",
                      type: "Excel",
                      size: "2MB",
                      createdAt: "2022-04-11T22:01:22",
                    },
                  ].map((row, idx) => (
                    <tr key={idx}>
                      <td className={TableClasses.td}>
                        <span className="text-gray-900">{row.name}</span>
                      </td>
                      <td className={TableClasses.td}>{row.type}</td>
                      <td className={TableClasses.td}>{row.size}</td>
                      <td className={TableClasses.td}>
                        <Time datetime={row.createdAt} />
                      </td>
                      <td className={TableClasses.td}>
                        <div className="flex items-center justify-end gap-6">
                          <Button
                            size="sm"
                            variant="white"
                            leadingIcon={
                              <DocumentDownloadIcon className="h-4" />
                            }
                          >
                            {t("Download")}
                          </Button>
                          <a
                            href=""
                            className="inline-flex items-center font-medium text-blue-600 hover:text-blue-900"
                          >
                            {t("Details")}{" "}
                            <ChevronRightIcon className="ml-1 h-4" />
                          </a>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Block>
          </section>

          {/* *********** Database *********** */}

          <section>
            <h3 className="mb-4 font-bold">{t("Postgres Data")}</h3>
            <Block>
              <table className={TableClasses.table}>
                <thead className={TableClasses.thead}>
                  <tr>
                    <th className={TableClasses.th}>{t("Name")}</th>
                    <th className={TableClasses.th}>{t("# Rows")}</th>
                    <th className={TableClasses.th}>{t("Created")}</th>
                    <th className={TableClasses.th}>
                      <span className="sr-only">{t("Actions")}</span>
                    </th>
                  </tr>
                </thead>
                <tbody className={TableClasses.tbody}>
                  {[
                    {
                      name: "cod_c19_clean",
                      nRows: "72348",
                      createdAt: "2022-03-21T10:00:00",
                    },
                    {
                      name: "bfa_malaria_consolidated",
                      nRows: "10211231",
                      createdAt: "2022-03-21T10:00:00",
                    },
                  ].map((row, idx) => (
                    <tr key={idx}>
                      <td className={TableClasses.td}>
                        <span className="text-gray-900">{row.name}</span>
                      </td>
                      <td className={TableClasses.td}>{row.nRows}</td>
                      <td className={TableClasses.td}>
                        <Time datetime={row.createdAt} />
                      </td>
                      <td className={TableClasses.td}>
                        <div className="flex items-center justify-end gap-6">
                          <Button
                            size="sm"
                            variant="white"
                            leadingIcon={
                              <DocumentDownloadIcon className="h-4" />
                            }
                          >
                            {t("Download")}
                          </Button>
                          <a
                            href=""
                            className="inline-flex items-center font-medium text-blue-600 hover:text-blue-900"
                          >
                            {t("Details")}{" "}
                            <ChevronRightIcon className="ml-1 h-4" />
                          </a>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Block>
          </section>

          {/* *********** Notebooks *********** */}

          <section>
            <h3 className="mb-4 font-bold">{t("Notebooks")}</h3>
            <Block>
              <table className={TableClasses.table}>
                <thead className={TableClasses.thead}>
                  <tr>
                    <th className={TableClasses.th}>{t("Name")}</th>
                    <th className={TableClasses.th}>{t("Type")}</th>
                    <th className={TableClasses.th}>{t("Created")}</th>
                    <th className={TableClasses.th}>
                      <span className="sr-only">{t("Actions")}</span>
                    </th>
                  </tr>
                </thead>
                <tbody className={TableClasses.tbody}>
                  {[
                    {
                      name: "cleanup.ipynb",
                      type: "Python notebook",
                      createdAt: "2022-04-01T11:32:11",
                    },
                    {
                      name: "tracker_analysis.ipynb",
                      type: "R notebook",
                      createdAt: "2022-04-03T14:32:01",
                    },
                    {
                      name: "build_dashboard.ipynb",
                      type: "Python notebook",
                      createdAt: "2022-04-17T22:03:15",
                    },
                  ].map((row, idx) => (
                    <tr key={idx}>
                      <td className={TableClasses.td}>
                        <span className="text-gray-900">{row.name}</span>
                      </td>
                      <td className={TableClasses.td}>{row.type}</td>
                      <td className={TableClasses.td}>
                        <Time datetime={row.createdAt} />
                      </td>
                      <td className={TableClasses.td}>
                        <div className="flex items-center justify-end gap-6">
                          <Button
                            size="sm"
                            variant="white"
                            leadingIcon={<ExternalLinkIcon className="h-4" />}
                          >
                            {t("Open notebook")}
                          </Button>
                          <a
                            href=""
                            className="inline-flex items-center font-medium text-blue-600 hover:text-blue-900"
                          >
                            {t("Details")}{" "}
                            <ChevronRightIcon className="ml-1 h-4" />
                          </a>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Block>
          </section>

          {/* *********** Visualizations *********** */}

          <section>
            <h3 className="mb-4 font-bold">{t("Visualizations")}</h3>
            <Block>
              <table className={TableClasses.table}>
                <thead className={TableClasses.thead}>
                  <tr>
                    <th className={TableClasses.th}>{t("Name")}</th>
                    <th className={TableClasses.th}>{t("Type")}</th>
                    <th className={TableClasses.th}>{t("Created")}</th>
                    <th className={TableClasses.th}>
                      <span className="sr-only">{t("Actions")}</span>
                    </th>
                  </tr>
                </thead>
                <tbody className={TableClasses.tbody}>
                  {[
                    {
                      name: "C19 surveillance dashboard",
                      type: "Tableau dashboard",
                      createdAt: "2022-04-01T10:37:58",
                    },
                    {
                      name: "Accessibility dashboard",
                      type: "AccessMod accessibility map",
                      createdAt: "2022-11-01T11:45:45",
                    },
                    {
                      name: "Malaria vaccination campaign",
                      type: "PowerBI dashboard",
                      createdAt: "2022-12-01T13:21:09",
                    },
                  ].map((row, idx) => (
                    <tr key={idx}>
                      <td className={TableClasses.td}>
                        <span className="text-gray-900">{row.name}</span>
                      </td>
                      <td className={TableClasses.td}>{row.type}</td>
                      <td className={TableClasses.td}>
                        <Time datetime={row.createdAt} />
                      </td>
                      <td className={TableClasses.td}>
                        <div className="flex items-center justify-end gap-6">
                          <Button
                            size="sm"
                            variant="white"
                            leadingIcon={<ExternalLinkIcon className="h-4" />}
                          >
                            {t("Open dashboard")}
                          </Button>
                          <a
                            href=""
                            className="inline-flex items-center font-medium text-blue-600 hover:text-blue-900"
                          >
                            {t("Details")}{" "}
                            <ChevronRightIcon className="ml-1 h-4" />
                          </a>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
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
});

export default CollectionPage;
