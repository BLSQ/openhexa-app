import { ArrowRightOnRectangleIcon } from "@heroicons/react/24/solid";
import Block from "core/components/Block";
import Button from "core/components/Button";
import DescriptionList, {
  DescriptionListDisplayMode,
} from "core/components/DescriptionList";
import Page from "core/components/Page";
import Time from "core/components/Time";
import User from "core/features/User";
import { createGetServerSideProps } from "core/helpers/page";
import useToggle from "core/hooks/useToggle";
import DefaultLayout from "core/layouts/default";
import DisableTwoFactorDialog from "identity/features/DisableTwoFactorDialog";
import EnableTwoFactorDialog from "identity/features/EnableTwoFactorDialog";
import {
  AccountPageDocument,
  AccountPageQuery,
  useAccountPageQuery,
} from "identity/graphql/queries.generated";
import { logout } from "identity/helpers/auth";
import useFeature from "identity/hooks/useFeature";
import { useTranslation } from "next-i18next";

function AccountPage() {
  const { t } = useTranslation();
  const { data } = useAccountPageQuery();
  const [twoFactorEnabled] = useFeature("two_factor");
  const [showTwoFactorDialog, { toggle: toggleTwoFactorDialog }] = useToggle();

  if (!data?.me.user) {
    return null;
  }

  const { user } = data.me;
  return (
    <>
      <Page title={t("Account")}>
        <DefaultLayout.PageContent className="my-6">
          <Block className="divide-y divide-gray-100">
            <Block.Header className="flex items-center justify-between">
              <User user={user} />
              <Button
                variant="primary"
                onClick={() => logout()}
                leadingIcon={<ArrowRightOnRectangleIcon className="h-4 w-4" />}
              >
                {t("Logout")}
              </Button>
            </Block.Header>
            <Block.Content>
              <DescriptionList
                columns={2}
                displayMode={DescriptionListDisplayMode.LABEL_ABOVE}
              >
                <DescriptionList.Item label={t("First name")}>
                  {user.firstName}
                </DescriptionList.Item>
                <DescriptionList.Item label={t("Last name")}>
                  {user.lastName}
                </DescriptionList.Item>
                <DescriptionList.Item label={t("Email")}>
                  {user.email}
                </DescriptionList.Item>
                <DescriptionList.Item label={t("Joined")}>
                  <Time relative datetime={user.dateJoined} />
                </DescriptionList.Item>
              </DescriptionList>
            </Block.Content>
            {twoFactorEnabled && (
              <Block.Section title={t("Security")} collapsible={false}>
                <DescriptionList
                  columns={2}
                  displayMode={DescriptionListDisplayMode.LABEL_ABOVE}
                >
                  <DescriptionList.Item label={t("Two-Factor Authentication")}>
                    <Button size="sm" onClick={toggleTwoFactorDialog}>
                      {data.me.hasTwoFactorEnabled ? t("Disable") : t("Setup")}
                    </Button>
                  </DescriptionList.Item>
                </DescriptionList>
              </Block.Section>
            )}
          </Block>
        </DefaultLayout.PageContent>
      </Page>

      {data.me.hasTwoFactorEnabled ? (
        <DisableTwoFactorDialog
          open={showTwoFactorDialog}
          onClose={toggleTwoFactorDialog}
        />
      ) : (
        <EnableTwoFactorDialog
          open={showTwoFactorDialog}
          onClose={toggleTwoFactorDialog}
        />
      )}
    </>
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
