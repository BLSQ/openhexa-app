import { FormInstance } from "core/hooks/useForm";
import { ConnectionForm } from "./utils";
import { useTranslation } from "react-i18next";
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
          description={t("The base url to access the API. It ends with /api/")}
          placeholder="https://play.dhis2.org/2.35.3/api/"
          label={t("API URL")}
        />
      </div>

      <Field
        onChange={form.handleInputChange}
        value={form.formData.username}
        name="username"
        label={t("Username")}
        placeholder="admin"
        required
      />

      <Field
        onChange={form.handleInputChange}
        value={form.formData.password}
        name="password"
        label={t("Password")}
        placeholder="district"
        required
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
