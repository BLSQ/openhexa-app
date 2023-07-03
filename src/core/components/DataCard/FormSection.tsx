import {
  ChevronDownIcon,
  ChevronRightIcon,
  PencilIcon,
} from "@heroicons/react/24/outline";

import { BlockSection } from "core/components/Block";
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
import Button from "../Button/Button";
import DescriptionList, { DescriptionListProps } from "../DescriptionList";
import DisableClickPropagation from "../DisableClickPropagation";
import Spinner from "../Spinner";
import { DataCardSectionContext } from "./context";
import { Property, PropertyDefinition, PropertyFlag } from "./types";

export type OnSaveFn = (
  values: { [key: string]: any },
  item: ItemInstance
) => Promise<void> | void;

type FormSectionProps = {
  editLabel?: string;
  editIcon?: ReactElement;
  onSave?: OnSaveFn;
  title?: string;
  children: ReactNode;
} & Pick<DescriptionListProps, "displayMode" | "columns"> &
  Omit<React.ComponentProps<typeof BlockSection>, "title" | "children">;

function getPropertyFlag<F>(
  flag: PropertyFlag | undefined,
  displayValue: any,
  isEdited: boolean = false,
  form: FormInstance<F>
) {
  if (typeof flag === "function") {
    return flag(displayValue, isEdited, form.formData);
  }
  return flag;
}

function getProperty<F>(
  definition: PropertyDefinition,
  item: ItemInstance,
  form: FormInstance<F>,
  isEdited: boolean
) {
  const displayValue = getValue(item, definition.accessor);
  const prop: Property = {
    displayValue,
    defaultValue: definition.defaultValue,
    formValue: form.formData[definition.id as keyof F],
    validate: definition.validate,
    setValue: (value: any) =>
      form.setFieldValue(definition.id as keyof F, value),
    id: definition.id,
    label: definition.label,
    help: definition.help,
    hideLabel: definition.hideLabel ?? false,
    readonly:
      getPropertyFlag<F>(definition.readonly, displayValue, isEdited, form) ??
      false,
    required:
      getPropertyFlag<F>(definition.required, displayValue, isEdited, form) ??
      false,
    visible:
      getPropertyFlag<F>(definition.visible, displayValue, isEdited, form) ??
      true,
  };
  return prop;
}

function FormSection<F extends { [key: string]: any }>(
  props: FormSectionProps
) {
  const { t } = useTranslation();
  const {
    title,
    editLabel,
    editIcon,
    className,
    displayMode,
    columns,
    collapsible,
    defaultOpen,
    children,
    onSave,
  } = props;
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
        if (property.validate) {
          const error = property.validate(values[property.id], values);
          if (error) {
            errors[property.id] = error;
          }
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
      acc[def.id] = getProperty<F>(def, item, form, isEdited);
      return acc;
    }, {});
    // form.validate();
  }, [definitions, item, form, form.formData, isEdited]);

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
      return getProperty(definition, item, form, isEdited);
    },
  };

  return (
    <DataCardSectionContext.Provider value={section}>
      <BlockSection
        collapsible={collapsible}
        defaultOpen={defaultOpen}
        className={className}
        title={({ open }) => (
          <>
            <h4 className="font-medium">{title}</h4>
            {onSave && open && !isEdited && (
              <DisableClickPropagation>
                <button
                  className="ml-4 inline-flex items-center gap-1 text-sm text-blue-500 hover:text-blue-400"
                  onClick={toggleEdit}
                >
                  {editLabel ?? t("Edit")}
                  {editIcon ?? <PencilIcon className="h-4" />}
                </button>
              </DisableClickPropagation>
            )}
            <div className="flex flex-1 flex-shrink items-center justify-end">
              {collapsible && (
                <button title={open ? t("Hide") : t("Show")}>
                  {open ? (
                    <ChevronDownIcon className="h-5 w-5" />
                  ) : (
                    <ChevronRightIcon className="h-5 w-5" />
                  )}
                </button>
              )}
            </div>
          </>
        )}
      >
        {() =>
          isEdited ? (
            <form onSubmit={form.handleSubmit}>
              <DescriptionList columns={columns} displayMode={displayMode}>
                {children}
              </DescriptionList>

              {form.submitError && (
                <p className={"my-2 text-sm text-red-600"}>
                  {form.submitError}
                </p>
              )}
              <div className="mt-6 flex items-center justify-end gap-2">
                <Button type="submit" disabled={form.isSubmitting}>
                  {form.isSubmitting && <Spinner size="xs" className="mr-1" />}
                  {t("Save")}
                </Button>
                <Button onClick={toggleEdit} variant="white">
                  {t("Cancel")}
                </Button>
              </div>
            </form>
          ) : (
            <DescriptionList columns={columns} displayMode={displayMode}>
              {children}
            </DescriptionList>
          )
        }
      </BlockSection>
    </DataCardSectionContext.Provider>
  );
}

export default FormSection;
