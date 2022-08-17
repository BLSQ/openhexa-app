import { createCollection } from "collections/helpers/collections";
import { CountryPicker_CountryFragment } from "core/features/CountryPicker/CountryPicker.generated";
import useForm from "core/hooks/useForm";
import { Collection } from "graphql-types";
import { useTranslation } from "next-i18next";

export type CollectionForm = {
  countries: CountryPicker_CountryFragment[] | null;
  name: string;
  tags: any[];
};

type AfterSubmitFn = (collection: { id: string }) => void;

function useCollectionForm(onAfterSubmit?: AfterSubmitFn) {
  const { t } = useTranslation();
  const form = useForm<CollectionForm, Pick<Collection, "id">>({
    async onSubmit(values) {
      const collection = await createCollection({
        name: values.name,
        countries: values.countries?.map((country) => ({
          code: country.code,
        })),
      });
      if (onAfterSubmit) {
        onAfterSubmit(collection);
      }
    },
    initialState: {
      countries: [],
      name: "",
    },
    validate(values) {
      const errors = {} as any;
      if (!values.name) {
        errors.name = t("Type a name for the collection");
      }
      return errors;
    },
  });

  return form;
}

export default useCollectionForm;
