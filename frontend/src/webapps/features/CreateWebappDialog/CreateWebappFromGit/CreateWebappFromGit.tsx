import Field from "core/components/forms/Field/Field";
import { useTranslation } from "next-i18next";

export type GitFormData = {
  name: string;
  url: string;
};

type CreateWebappFromGitProps = {
  values: GitFormData;
  onChange: (values: GitFormData) => void;
};

const CreateWebappFromGit = ({
  values,
  onChange,
}: CreateWebappFromGitProps) => {
  const { t } = useTranslation();

  return (
    <div className="space-y-6">
      <p className="text-sm text-gray-500">
        {t(
          "Import an existing web app from a Git repository. OpenHEXA clones the repository and serves it as a web app.",
        )}
      </p>
      <div className="grid gap-6">
        <Field
          name="name"
          label={t("Name")}
          required
          placeholder={t("My Web App")}
          value={values.name}
          onChange={(e) => onChange({ ...values, name: e.target.value })}
        />
        <Field
          name="url"
          label={t("Repository URL")}
          required
          placeholder="https://github.com/my-org/my-webapp.git"
          value={values.url}
          onChange={(e) => onChange({ ...values, url: e.target.value })}
        />
      </div>
    </div>
  );
};

export default CreateWebappFromGit;
