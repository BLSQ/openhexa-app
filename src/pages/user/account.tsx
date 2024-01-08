import { ArrowRightOnRectangleIcon } from "@heroicons/react/24/solid";
import Block from "core/components/Block";
import Button from "core/components/Button";
import DataCard from "core/components/DataCard";
import DateProperty from "core/components/DataCard/DateProperty";
import { OnSaveFn } from "core/components/DataCard/FormSection";
import RenderProperty from "core/components/DataCard/RenderProperty";
import TextProperty from "core/components/DataCard/TextProperty";
import { BaseColumn } from "core/components/DataGrid";
import DataGrid from "core/components/DataGrid/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import DescriptionList, {
  DescriptionListDisplayMode,
} from "core/components/DescriptionList";
import Page from "core/components/Page";
import SimpleSelect from "core/components/forms/SimpleSelect";
import { AlertType, displayAlert } from "core/helpers/alert";
import { LANGUAGES } from "core/helpers/i18n";
import { createGetServerSideProps } from "core/helpers/page";
import useToggle from "core/hooks/useToggle";
import BackLayout from "core/layouts/back";
import DisableTwoFactorDialog from "identity/features/DisableTwoFactorDialog";
import EnableTwoFactorDialog from "identity/features/EnableTwoFactorDialog";
import { useUpdateUserMutation } from "identity/graphql/mutations.generated";
import {
  AccountPageDocument,
  AccountPageQuery,
  useAccountPageQuery,
} from "identity/graphql/queries.generated";
import { logout } from "identity/helpers/auth";
import useFeature from "identity/hooks/useFeature";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import {
  useDeclineWorkspaceInvitationMutation,
  useJoinWorkspaceMutation,
} from "workspaces/graphql/mutations.generated";

function AccountPage() {
  const { t } = useTranslation();
  const { data, refetch } = useAccountPageQuery();
  const [twoFactorEnabled] = useFeature("two_factor");
  const [showTwoFactorDialog, { toggle: toggleTwoFactorDialog }] = useToggle();
  const router = useRouter();
  const [updateUser] = useUpdateUserMutation();

  const [joinWorkspace] = useJoinWorkspaceMutation();
  const [declineWorkspaceInvitation] = useDeclineWorkspaceInvitationMutation();

  async function doJoinWorkspace(invitationId: string) {
    const { data } = await joinWorkspace({
      variables: { input: { invitationId } },
    });
    if (!data?.joinWorkspace.success) {
      displayAlert(t("Failed to accept invitation"), AlertType.error);
    } else {
      refetch();
    }
  }

  async function doDeclineWorkspaceInvitation(invitationId: string) {
    if (
      !window.confirm(t("Are you sure you want to decline this invitation?"))
    ) {
      return;
    }
    const { data } = await declineWorkspaceInvitation({
      variables: { input: { invitationId } },
    });
    if (!data?.declineWorkspaceInvitation.success) {
      displayAlert(t("Failed to decline invitation"), AlertType.error);
    } else {
      refetch();
    }
  }

  if (!data?.me.user) {
    return null;
  }

  const onSave: OnSaveFn = async (values) => {
    const prevLanguage = data.me.user!.language;
    await updateUser({
      variables: {
        input: {
          firstName: values.firstName,
          lastName: values.lastName,
          language: values.language,
        },
      },
    });
    if (prevLanguage !== values.language) {
      router.reload();
    }
  };

  const { user } = data.me;
  return (
    <Page title={t("Account")}>
      <BackLayout
        className="gap-5 flex flex-col"
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
        <DataCard item={user} className="divide-y divide-gray-100">
          <DataCard.FormSection
            title={user.displayName}
            onSave={onSave}
            collapsible={false}
            displayMode={DescriptionListDisplayMode.LABEL_ABOVE}
            columns={2}
          >
            <TextProperty
              label={t("First name")}
              accessor="firstName"
              required
              id="firstName"
            />
            <TextProperty
              label={t("Last name")}
              accessor="lastName"
              required
              id="lastName"
            />
            <RenderProperty<keyof typeof LANGUAGES>
              id="language"
              accessor={"language"}
              label={t("Language")}
            >
              {(property, section) =>
                section.isEdited ? (
                  <SimpleSelect
                    value={property.formValue}
                    required
                    onChange={(e) =>
                      property.setValue(e.target.value as "en" | "fr")
                    }
                  >
                    {Object.entries(LANGUAGES).map(([key, value]) => (
                      <option key={key} value={key}>
                        {value}
                      </option>
                    ))}
                  </SimpleSelect>
                ) : (
                  <span>{LANGUAGES[property.displayValue]}</span>
                )
              }
            </RenderProperty>
            <TextProperty
              label={t("Email")}
              accessor="email"
              id="email"
              readonly
            />
            <DateProperty
              relative
              label={t("Joined")}
              accessor="dateJoined"
              id="dateJoined"
              readonly
            />
          </DataCard.FormSection>
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
        </DataCard>

        {data.pendingWorkspaceInvitations.totalItems > 0 ? (
          <Block>
            <Block.Header>{t("Pending invitations")}</Block.Header>
            <DataGrid
              totalItems={data.pendingWorkspaceInvitations.totalItems}
              data={data.pendingWorkspaceInvitations.items}
              fixedLayout={false}
            >
              <TextColumn
                accessor="workspace.name"
                label={t("Workspace")}
                id="workspace"
              />
              <TextColumn
                accessor="invitedBy.displayName"
                label={t("Invited by")}
                id="invitedBy"
              />
              <BaseColumn className="flex justify-end gap-x-2">
                {(invitation) => (
                  <>
                    <Button
                      onClick={() => doJoinWorkspace(invitation.id)}
                      size="sm"
                    >
                      {t("Accept")}
                    </Button>
                    <Button
                      onClick={() =>
                        doDeclineWorkspaceInvitation(invitation.id)
                      }
                      size="sm"
                      variant="danger"
                    >
                      {t("Decline")}
                    </Button>
                  </>
                )}
              </BaseColumn>
            </DataGrid>
          </Block>
        ) : null}
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
