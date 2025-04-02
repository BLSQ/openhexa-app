import { FormInstance } from "core/hooks/useForm";
import { useTranslation } from "next-i18next";
import { ConnectionForm } from "./utils";
import Field from "core/components/forms/Field";

function PostgreSQLForm(props: { form: FormInstance<ConnectionForm> }) {
  const { form } = props;
  const { t } = useTranslation();

  return (
    <>
      <Field
        onChange={form.handleInputChange}
        value={form.formData.db_name}
        name="db_name"
        label={t("Database name")}
        required
        fullWidth
      />
      <Field
        onChange={form.handleInputChange}
        value={form.formData.host}
        name="host"
        label={t("Host")}
        placeholder="Ex: 127.0.0.1"
        help={t("IP Address or domain name of the PostgreSQL server")}
        required
        fullWidth
      />
      <Field
        onChange={form.handleInputChange}
        value={form.formData.port}
        name="port"
        type="number"
        help={t("Port of the PostgreSQL server")}
        label={t("Port")}
        placeholder="5432"
        required
        fullWidth
      />

      <Field
        onChange={form.handleInputChange}
        value={form.formData.username}
        name="username"
        placeholder="postgres"
        help={t("Username to connect to the PostgreSQL server")}
        label={t("Username")}
        required
        fullWidth
      />

      <Field
        onChange={form.handleInputChange}
        value={form.formData.password}
        name="password"
        help={t("Password to connect to the PostgreSQL server")}
        label={t("Password")}
        required
        fullWidth
      />
    </>
  );
}

export default {
  label: "PostgreSQL",
  color: "bg-blue-300",
  iconSrc: "/static/connector_postgresql/img/symbol.svg",
  fields: [
    { code: "db_name", name: "Database name", required: true },
    { code: "host", name: "Host", required: true },
    { code: "port", name: "Port", defaultValue: "5432", required: true },
    { code: "username", name: "User", required: true },
    { code: "password", secret: true, name: "Password", required: true },
  ],
  Form: PostgreSQLForm,
};
