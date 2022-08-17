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
    <div className="grid grid-cols-2 gap-2">
      <Field
        type="text"
        name="name"
        label={t("Collection name")}
        value={formData.name}
        onChange={handleInputChange}
        required
      />
      <Field
        type="text"
        name="name"
        label={t("Countries")}
        onChange={handleInputChange}
      >
        <CountryPicker
          withPortal
          multiple
          value={formData.countries ?? null}
          onChange={(value) => setFieldValue("countries", value)}
        />
      </Field>
    </div>
  );
};

export default CollectionPartialForm;
