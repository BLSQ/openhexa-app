import { FormInstance } from "core/hooks/useForm";
import { ConnectionForm } from "./utils";
import { useTranslation } from "next-i18next";
import Field from "core/components/forms/Field/Field";
import Title from "core/components/Title";
import Textarea from "core/components/forms/Textarea/Textarea";

function GCSBucketForm(props: { form: FormInstance<ConnectionForm> }) {
  const { form } = props;
  const { t } = useTranslation();

  return (
    <>
      <Field
        onChange={form.handleInputChange}
        value={form.formData.bucket_name}
        name="bucket_name"
        label={t("Bucket name")}
        placeholder="hexa-my-bucket"
        required
        fullWidth
      />
      <div className="col-span-2">
        <Title level={6}>{t("Credentials")}</Title>
        <p className="text-sm text-gray-500">
          {t("The credentials are required and have to be in JSON format")}
        </p>
      </div>
      <Field
        required
        className="col-span-2"
        name="service_account_key"
        label={t("Service Account Key")}
        help={t("The service account key in JSON format")}
        fullWidth
      >
        <Textarea
          name="service_account_key"
          required
          onChange={form.handleInputChange}
        >
          {form.formData.service_account_key}
        </Textarea>
      </Field>
    </>
  );
}

export default {
  label: "Google GCS Bucket",
  color: "bg-blue-200",
  iconSrc: "/images/gcs.svg",
  Form: GCSBucketForm,
  fields: [
    { code: "bucket_name", name: "Bucket name", required: true },
    {
      code: "service_account_key",
      name: "Service Account Key",
      required: true,
      secret: true,
    },
  ],
};
