import DataCard from "core/components/DataCard";
import DateProperty from "core/components/DataCard/DateProperty";
import { DescriptionListDisplayMode } from "core/components/DescriptionList";
import { OnSaveFn } from "core/components/DataCard/FormSection";
import TextProperty from "core/components/DataCard/TextProperty";
import { useUpdateUserMutation } from "identity/graphql/mutations.generated";
import { User } from "graphql/types";
import { useTranslation } from "next-i18next";

type AccountProfileSettingsProps = {
  user: User;
};

const AccountProfileSettings = (props: AccountProfileSettingsProps) => {
  const { user } = props;
  const [updateUser] = useUpdateUserMutation();
  const { t } = useTranslation();

  const onSave: OnSaveFn = async (values) => {
    await updateUser({
      variables: {
        input: {
          firstName: values.firstName,
          lastName: values.lastName,
        },
      },
    });
  };

  return (
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
  )
}

export default AccountProfileSettings;
