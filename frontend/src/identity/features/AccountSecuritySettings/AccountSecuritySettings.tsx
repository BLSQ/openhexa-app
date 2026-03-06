import Block from "core/components/Block";
import Button from "core/components/Button";
import DescriptionList, {
  DescriptionListDisplayMode,
} from "core/components/DescriptionList";
import useToggle from "core/hooks/useToggle";
import DisableTwoFactorDialog from "identity/features/DisableTwoFactorDialog";
import EnableTwoFactorDialog from "identity/features/EnableTwoFactorDialog";
import { useTranslation } from "next-i18next";

type AccountSecuritySettingsProps = {
  hasTwoFactorEnabled: boolean;
};

const AccountSecuritySettings = (props: AccountSecuritySettingsProps) => {
  const { hasTwoFactorEnabled } = props;
  const [showTwoFactorDialog, { toggle: toggleTwoFactorDialog }] = useToggle();
  const { t } = useTranslation();

  return (
    <Block.Section title={t("Security")} collapsible={false}>
      <DescriptionList
        columns={2}
        displayMode={DescriptionListDisplayMode.LABEL_ABOVE}
      >
        <DescriptionList.Item label={t("Two-Factor Authentication")}>
          {hasTwoFactorEnabled
            ? t("Currently enabled")
            : t("Currently disabled")}
          <Button
            size="sm"
            className="ml-2"
            onClick={toggleTwoFactorDialog}
          >
            {hasTwoFactorEnabled ? t("Disable") : t("Enable")}
          </Button>
        </DescriptionList.Item>
      </DescriptionList>
      {hasTwoFactorEnabled ? (
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
    </Block.Section>
  )
}

export default AccountSecuritySettings;
