import { useTranslation } from "next-i18next";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import OrganizationLayout from "organizations/layouts/OrganizationLayout";
import {
  OrganizationDocument,
  OrganizationWithWorkspacesQuery,
  useOrganizationWithWorkspacesQuery,
} from "organizations/graphql/queries.generated";
import Page from "core/components/Page";
import Title from "core/components/Title";
import OrganizationExternalCollaborators from "organizations/features/OrganizationExternalCollaborators";
import OrganizationWorkspaceInvitations from "organizations/features/OrganizationWorkspaceInvitations";

type Props = {
  organization: OrganizationWithWorkspacesQuery["organization"];
};

const OrganizationExternalCollaboratorsPage: NextPageWithLayout<Props> = ({
  organization: SRROrganization,
}) => {
  const { t } = useTranslation();

  const { data: clientOrganization } = useOrganizationWithWorkspacesQuery({
    variables: { id: SRROrganization?.id },
    skip: !SRROrganization?.id,
  });

  const organization = clientOrganization?.organization || SRROrganization;

  if (!organization) {
    return null;
  }

  return (
    <Page title={t("External Collaborators")}>
      <OrganizationLayout
        organization={organization}
        header={
          <div>
            <h1 className="text-2xl font-bold">
              {t("External Collaborators")}
            </h1>
            <p className="text-sm text-gray-500">
              {organization.externalCollaborators.totalItems}{" "}
              {organization.externalCollaborators.totalItems === 1
                ? t(
                    "user with workspace access but without organization membership",
                  )
                : t(
                    "users with workspace access but without organization membership",
                  )}
            </p>
          </div>
        }
      >
        <OrganizationExternalCollaborators organizationId={organization.id} />
        <div className="mt-12">
          <Title level={2}>{t("Pending Direct Workspace Invitations")}</Title>
          <OrganizationWorkspaceInvitations organizationId={organization.id} />
        </div>
      </OrganizationLayout>
    </Page>
  );
};

OrganizationExternalCollaboratorsPage.getLayout = (page) => page;

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

export default OrganizationExternalCollaboratorsPage;
