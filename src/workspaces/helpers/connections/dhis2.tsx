import { FormInstance } from "core/hooks/useForm";
import { ConnectionForm } from "./utils";
import { useTranslation } from "next-i18next";
import Field from "core/components/forms/Field/Field";

function DHIS2Form(props: { form: FormInstance<ConnectionForm> }) {
  const { form } = props;
  const { t } = useTranslation();

  return (
    <>
      <div className="col-span-2">
        <Field
          onChange={form.handleInputChange}
          value={form.formData.url}
          name="url"
          type="url"
          required
          description={t(
            "The base URL of the DHIS2 server, without the /api suffix.",
          )}
          placeholder="https://play.dhis2.org/2.35.3"
          label={t("URL")}
          fullWidth
        />
      </div>

      <Field
        onChange={form.handleInputChange}
        value={form.formData.username}
        name="username"
        label={t("Username")}
        placeholder="admin"
        required
        fullWidth
      />

      <Field
        onChange={form.handleInputChange}
        value={form.formData.password}
        name="password"
        label={t("Password")}
        placeholder="district"
        required
        fullWidth
      />
    </>
  );
}

export default {
  label: "DHIS2 Instance",
  color: "bg-pink-300",
  iconSrc: "/images/dhis2.svg",
  Form: DHIS2Form,
  fields: [
    { code: "url", name: "URL", required: true },
    { code: "username", name: "Username", required: true },
    { code: "password", secret: true, name: "Password", required: true },
  ],
};
