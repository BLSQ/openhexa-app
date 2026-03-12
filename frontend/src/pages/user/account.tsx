import { ArrowRightOnRectangleIcon } from "@heroicons/react/24/solid";
import Button from "core/components/Button";
import DataCard from "core/components/DataCard";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import BackLayout from "core/layouts/back";
import {
  AccountPageDocument,
  AccountPageQuery,
  useAccountPageQuery,
} from "identity/graphql/queries.generated";
import { logout } from "identity/helpers/auth";
import { useTranslation } from "next-i18next";
import AccountAiSettings from "identity/features/AccountAiSettings";
import AccountProfileSettings from "identity/features/AccountProfileSettings";
import AccountSecuritySettings from "identity/features/AccountSecuritySettings";
import useFeature from "identity/hooks/useFeature";
import PendingWorkspaceInvitations from "../../identity/features/PendingWorkspaceInvitations";

function AccountPage() {
  const { t } = useTranslation();
  const { data, refetch } = useAccountPageQuery();
  const [isAssistantEnabled] = useFeature("assistant");

  if (!data?.me.user) {
    return null;
  }

  const { user } = data.me;
  return (
    <Page title={t("Account")}>
      <BackLayout
        className="gap-5 flex flex-col"
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
        <DataCard item={user} className="divide-y divide-gray-100">
          <AccountProfileSettings user={user} />
          <AccountSecuritySettings hasTwoFactorEnabled={data.me.hasTwoFactorEnabled} />
          {isAssistantEnabled && (
            <AccountAiSettings
              settings={user.aiSettings}
              labels={data.aiLabels}
              monthlyCost={data.me.assistantMonthlyCost}
              totalCost={data.me.assistantTotalCost}
              refetch={refetch}
            />
          )}
        </DataCard>

        <PendingWorkspaceInvitations invitations={data.pendingWorkspaceInvitations} />
      </BackLayout>
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
