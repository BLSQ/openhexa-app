import { PencilIcon } from "@heroicons/react/outline";
import useForm, { FormInstance } from "core/hooks/useForm";
import {
  getValue,
  ItemInstance,
  useItemContext,
} from "core/hooks/useItemContext";
import _ from "lodash";
import { useTranslation } from "next-i18next";
import {
  ReactElement,
  ReactNode,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import Block from "../Block";
import Button from "../Button";
import DescriptionList from "../DescriptionList";
import Spinner from "../Spinner";
import { DataCardSectionContext } from "./context";
import { Property, PropertyDefinition, PropertyFlag } from "./types";

export type OnSaveFn = (
  values: { [key: string]: any },
  item: ItemInstance
) => Promise<void> | void;

type SectionProps = {
  className?: string;
  children?: ReactNode;
  title?: string;
  editLabel?: string;
  editIcon?: ReactElement;
  onSave?: OnSaveFn;
};

const getPropertyFlag = (displayValue: any, flag?: PropertyFlag) => {
  if (typeof flag === "function") {
    return flag(displayValue);
  }
  return flag;
};

function getProperty<F>(
  definition: PropertyDefinition,
  item: ItemInstance,
  form: FormInstance<F>
) {
  const displayValue = getValue(item, definition.accessor);
  const prop: Property = {
    displayValue,
    formValue: form.formData[definition.id as keyof F],
    setValue: (value: any) =>
      form.setFieldValue(definition.id as keyof F, value),
    id: definition.id,
    label: definition.label,
    readonly: getPropertyFlag(displayValue, definition.readonly) ?? false,
    required: getPropertyFlag(displayValue, definition.required) ?? false,
    visible: getPropertyFlag(displayValue, definition.visible) ?? true,
  };
  return prop;
}

function Section<F = { [key: string]: any }>(props: SectionProps) {
  const { t } = useTranslation();
  const { title, editLabel, editIcon, className, children, onSave } = props;
  const { item } = useItemContext();

  const [isEdited, setEdited] = useState<boolean>(false);
  const toggleEdit = useCallback(() => setEdited((isEdited) => !isEdited), []);

  const definitions = useRef<PropertyDefinition[]>([]);
  const properties = useRef<{ [key: Property["id"]]: Property }>({});

  const form = useForm<F>({
    getInitialState() {
      const initialState = {} as any;
      Object.entries(properties.current).forEach(([key, prop]) => {
        initialState[key] = prop.displayValue;
      });
      return initialState;
    },
    onSubmit: async (values) => {
      if (onSave) {
        await onSave(values, item);
      }
      setEdited(false);
    },
    validate(values) {
      const errors = {} as any;

      for (const property of Object.values(properties.current)) {
        if (property.required && !values[property.id]) {
          errors[property.id] = t("This field is required");
        }
      }

      return errors;
    },
  });

  useEffect(() => {
    if (isEdited) {
      form.resetForm();
    }
  }, [form, isEdited]);

  useEffect(() => {
    properties.current = definitions.current.reduce<{
      [key: string]: Property;
    }>((acc, def) => {
      acc[def.id] = getProperty<F>(def, item, form);
      return acc;
    }, {});
  }, [definitions, item, form]);

  const section = {
    item,
    isEdited,
    toggleEdit,
    properties: properties.current,
    form,
    setProperty(definition: PropertyDefinition) {
      const existingDefinition = definitions.current.find(
        (x) => x.id === definition.id
      );
      if (!_.isEqual(definition, existingDefinition)) {
        definitions.current = definitions.current
          .filter((d) => d.id !== definition.id)
          .concat(definition);
      }
      return getProperty(definition, item, form);
    },
  };

  return (
    <DataCardSectionContext.Provider value={section}>
      <Block.Content className={className}>
        <h4 className="mb-4">
          <span className=" font-medium">{title}</span>
          {onSave && !isEdited && (
            <button
              className="ml-4 inline-flex items-center gap-1 text-sm text-blue-500 hover:text-blue-400"
              onClick={toggleEdit}
            >
              {editLabel ?? t("Edit")}
              {editIcon ?? <PencilIcon className="h-4" />}
            </button>
          )}
        </h4>
        <form onSubmit={form.handleSubmit}>
          <DescriptionList>{children}</DescriptionList>

          {isEdited && (
            <>
              {form.submitError && (
                <p className={"my-2 text-sm text-red-600"}>
                  {form.submitError}
                </p>
              )}
              <div className="mt-2 flex items-center justify-end gap-2">
                <Button
                  type="submit"
                  disabled={form.isSubmitting || !form.isValid}
                >
                  {form.isSubmitting && <Spinner size="xs" className="mr-1" />}
                  {t("Save")}
                </Button>
                <Button onClick={toggleEdit} variant="white">
                  {t("Cancel")}
                </Button>
              </div>
            </>
          )}
        </form>
      </Block.Content>
    </DataCardSectionContext.Provider>
  );
}

export default Section;
