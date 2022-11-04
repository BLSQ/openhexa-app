import { ArrowRightOnRectangleIcon } from "@heroicons/react/24/solid";
import Button from "core/components/Button";
import DataCard from "core/components/DataCard";
import DateProperty from "core/components/DataCard/DateProperty";
import TextProperty from "core/components/DataCard/TextProperty";
import { DescriptionListDisplayMode } from "core/components/DescriptionList";
import Page from "core/components/Layout/Page";
import { PageContent } from "core/components/Layout/PageContent";
import User from "core/features/User";
import { User_UserFragment } from "core/features/User/User.generated";
import { createGetServerSideProps } from "core/helpers/page";
import {
  AccountPageDocument,
  AccountPageQuery,
  useAccountPageQuery,
} from "identity/graphql/queries.generated";
import { logout } from "identity/helpers/auth";
import { useTranslation } from "next-i18next";

function AccountPage() {
  const { t } = useTranslation();

  const { data } = useAccountPageQuery();
  if (!data) {
    return null;
  }

  return (
    <Page>
      <PageContent title={t("Account")} className="my-6">
        <DataCard item={data.me.user}>
          <DataCard.Heading<User_UserFragment>
            renderActions={(item) => (
              <Button
                variant="primary"
                onClick={() => logout("/")}
                leadingIcon={<ArrowRightOnRectangleIcon className="h-4 w-4" />}
              >
                {t("Logout")}
              </Button>
            )}
          >
            {(item) => <User user={item} />}
          </DataCard.Heading>
          <DataCard.Section
            displayMode={DescriptionListDisplayMode.LABEL_ABOVE}
            columns={2}
          >
            <TextProperty
              id="firstName"
              label={t("First name")}
              accessor="firstName"
            />
            <TextProperty
              id="lastName"
              label={t("Last name")}
              accessor="lastName"
            />
            <TextProperty id="email" label={t("Email")} accessor="email" />
            <DateProperty
              relative
              id="joinedAt"
              label={t("Joined")}
              accessor="dateJoined"
            />
          </DataCard.Section>
        </DataCard>
      </PageContent>
    </Page>
  );
}

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    const { data } = await client.query<AccountPageQuery>({
      query: AccountPageDocument,
    });

    if (!data.me.user) {
      return {
        notFound: true,
      };
    }
  },
});

export default AccountPage;
