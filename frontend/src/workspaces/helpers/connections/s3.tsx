import { FormInstance } from "core/hooks/useForm";
import { ConnectionForm } from "./utils";
import { useTranslation } from "next-i18next";
import Field from "core/components/forms/Field/Field";
import Title from "core/components/Title";

function S3BucketForm(props: { form: FormInstance<ConnectionForm> }) {
  const { form } = props;
  const { t } = useTranslation();

  return (
    <>
      <Field
        onChange={form.handleInputChange}
        value={form.formData.bucket_name}
        name="bucket_name"
        label={t("Bucket name")}
        required
        fullWidth
      />
      <div className="col-span-2">
        <Title level={6}>{t("Credentials")}</Title>
        <p className="text-sm text-gray-500">
          {t(
            "The credentials are required if the bucket cannot be accessed publicly.",
          )}
        </p>
      </div>
      <Field
        onChange={form.handleInputChange}
        value={form.formData.access_key_id}
        name="access_key_id"
        label={t("Access key ID")}
        help={t(
          'The "Access key ID" of the AWS user with access to the bucket. This can be found in the AWS console.',
        )}
        fullWidth
      />

      <Field
        onChange={form.handleInputChange}
        value={form.formData.access_key_secret}
        name="access_key_secret"
        label={t("Secret access key")}
        help={t(
          'The "secret access key" of the AWS user with access to the bucket. This can be found in the AWS console.',
        )}
        fullWidth
      />
    </>
  );
}

export default {
  label: "Amazon S3 Bucket",
  color: "bg-orange-200",
  iconSrc: "/images/s3.svg",

  fields: [
    { code: "bucket_name", name: "Bucket name", required: true },
    { code: "access_key_id", name: "Access key ID" },
    { code: "access_key_secret", name: "Secret access key", secret: true },
  ],
  Form: S3BucketForm,
};
