import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import OrganizationLayout from "../../../organizations/layouts/OrganizationLayout";
import { useTranslation } from "next-i18next";
import Page from "core/components/Page";
import Link from "core/components/Link";
import Flag from "react-world-flags";
import { GlobeAltIcon } from "@heroicons/react/24/outline";
import {
  OrganizationDocument,
  OrganizationQuery,
} from "organizations/graphql/queries.generated";

type Props = {
  organization: OrganizationQuery["organization"];
};

const OrganizationPage: NextPageWithLayout<Props> = ({ organization }) => {
  const { t } = useTranslation();

  if (!organization) {
    return null;
  }

  const totalWorkspaces = organization.workspaces.items.length;
  return (
    <Page title={t("Organization")}>
      <OrganizationLayout organization={organization}>
        <div className="p-6">
          <div className="m-8">
            <h1 className="text-4xl font-bold">{organization.name}</h1>
            <p className="text-lg mt-2 text-gray-500">
              {totalWorkspaces}{" "}
              {totalWorkspaces > 1 ? t("workspaces") : t("workspace")}
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 m-8">
            {organization.workspaces.items.map((ws) => (
              <Link
                key={ws.slug}
                href={`/workspaces/${ws.slug}`}
                className="font-medium mt-2 block text-gray-800"
                noStyle
              >
                <div className="hover:scale-105 bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 flex items-center gap-2">
                  <div className="flex h-full w-5 items-center">
                    {ws.countries && ws.countries.length === 1 ? (
                      <Flag
                        code={ws.countries[0].code}
                        className="w-5 shrink rounded-xs"
                      />
                    ) : (
                      <GlobeAltIcon className="w-5 shrink rounded-xs text-gray-400" />
                    )}
                  </div>
                  <div>{ws.name}</div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </OrganizationLayout>
    </Page>
  );
};

OrganizationPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await OrganizationLayout.prefetch(ctx);
    const { data } = await client.query({
      query: OrganizationDocument,
      variables: {
        id: ctx.params?.organizationId as string,
      },
    });

    if (!data?.organization) {
      return {
        notFound: true,
      };
    }

    return {
      props: {
        organization: data.organization,
      },
    };
  },
});

export default OrganizationPage;
