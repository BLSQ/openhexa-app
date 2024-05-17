import { FormInstance } from "core/hooks/useForm";
import { ConnectionForm } from "./utils";
import { useTranslation } from "next-i18next";
import Field from "core/components/forms/Field/Field";

function IASOForm(props: { form: FormInstance<ConnectionForm> }) {
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
          placeholder="https://iaso.bluesquare.org"
          label={t("Iaso Instance URL")}
          help={t("The base url to access the Iaso instance.")}
          fullWidth
        />
      </div>

      <Field
        onChange={form.handleInputChange}
        value={form.formData.username}
        name="username"
        label={t("Username")}
        required
        fullWidth
      />

      <Field
        onChange={form.handleInputChange}
        value={form.formData.password}
        name="password"
        label={t("Password")}
        required
        fullWidth
      />
    </>
  );
}

export default {
  label: "IASO Account",
  color: "bg-green-300",
  iconSrc: "/images/iaso.svg",
  Form: IASOForm,
  fields: [
    { code: "url", name: "IASO Instance URL", required: true },
    { code: "username", name: "Username", required: true },
    { code: "password", secret: true, name: "Password", required: true },
  ],
};
