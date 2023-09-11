import { ArrowRightOnRectangleIcon } from "@heroicons/react/24/solid";
import Block from "core/components/Block";
import Button from "core/components/Button";
import DescriptionList, {
  DescriptionListDisplayMode,
} from "core/components/DescriptionList";
import Page from "core/components/Page";
import Time from "core/components/Time";
import { createGetServerSideProps } from "core/helpers/page";
import useToggle from "core/hooks/useToggle";
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
import BackLayout from "core/layouts/back";
import { useRouter } from "next/router";

function AccountPage() {
  const { t } = useTranslation();
  const { data } = useAccountPageQuery();
  const [twoFactorEnabled] = useFeature("two_factor");
  const [showTwoFactorDialog, { toggle: toggleTwoFactorDialog }] = useToggle();
  const router = useRouter();
  if (!data?.me.user) {
    return null;
  }

  const { user } = data.me;
  return (
    <Page title={t("Account")}>
      <BackLayout
        onBack={() => router.back()}
        title={
          <div className={"flex justify-between items-center gap-3"}>
            {t("Your account")}
            <Button
              variant="primary"
              onClick={() => logout()}
              leadingIcon={<ArrowRightOnRectangleIcon className="h-4 w-4" />}
            >
              {t("Logout")}
            </Button>
          </div>
        }
      >
        <Block className="divide-y divide-gray-100">
          <Block.Header>{user.displayName}</Block.Header>
          <Block.Content>
            <DescriptionList
              columns={2}
              displayMode={DescriptionListDisplayMode.LABEL_ABOVE}
            >
              <DescriptionList.Item label={t("First name")}>
                {user.firstName || "-"}
              </DescriptionList.Item>
              <DescriptionList.Item label={t("Last name")}>
                {user.lastName || "-"}
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
                  {data.me.hasTwoFactorEnabled
                    ? t("Currently enabled")
                    : t("Currently disabled")}
                  <Button
                    size="sm"
                    className="ml-2"
                    onClick={toggleTwoFactorDialog}
                  >
                    {data.me.hasTwoFactorEnabled ? t("Disable") : t("Enable")}
                  </Button>
                </DescriptionList.Item>
              </DescriptionList>
            </Block.Section>
          )}
        </Block>
      </BackLayout>

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
    </Page>
  );
}

AccountPage.getLayout = (page: any) => page;

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
