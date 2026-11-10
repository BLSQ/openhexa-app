import Field from "core/components/forms/Field";
import SimpleSelect from "core/components/forms/SimpleSelect";
import { LANGUAGES } from "core/helpers/i18n";
import { useTranslation } from "next-i18next";

type InvitationLanguageFieldProps = {
  value?: string;
  onChange(language: string): void;
};

const InvitationLanguageField = ({
  value,
  onChange,
}: InvitationLanguageFieldProps) => {
  const { t } = useTranslation();

  return (
    <Field
      name="language"
      label={t("Invitation language")}
      description={t(
        "Language of the invitation email for people without an account. Existing users receive it in their own language.",
      )}
      required
    >
      <SimpleSelect
        id="language"
        name="language"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required
      >
        {Object.entries(LANGUAGES).map(([code, label]) => (
          <option key={code} value={code}>
            {label}
          </option>
        ))}
      </SimpleSelect>
    </Field>
  );
};

export default InvitationLanguageField;
