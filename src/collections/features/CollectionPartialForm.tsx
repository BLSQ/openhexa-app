import useCollectionForm from "collections/hooks/useCollectionForm";
import Field from "core/components/forms/Field";
import CountryPicker from "core/features/CountryPicker";
import { useTranslation } from "next-i18next";

type CollectionPartialFormProps = {
  form: ReturnType<typeof useCollectionForm>;
};

const CollectionPartialForm = (props: CollectionPartialFormProps) => {
  const { form } = props;
  const { t } = useTranslation();
  const { formData, handleInputChange, setFieldValue } = form;

  return (
    <div className="grid grid-cols-4 gap-4">
      <Field
        type="text"
        name="name"
        label={t("Name")}
        value={formData.name}
        onChange={handleInputChange}
        className="col-span-4"
        required
      />
      <Field
        name="summary"
        value={formData.summary}
        onChange={form.handleInputChange}
        label={t("Summary")}
        className="col-span-4"
      />
      <Field
        name="countries"
        label={t("Countries")}
        onChange={handleInputChange}
        className="col-span-4"
      >
        <CountryPicker
          withPortal
          multiple
          value={formData.countries ?? undefined}
          onChange={(value) => setFieldValue("countries", value)}
        />
      </Field>
    </div>
  );
};

export default CollectionPartialForm;
