import { FormInstance } from "core/hooks/useForm";
import { ValueAccessor } from "core/hooks/useItemContext";

export type PropertyFlag =
  | boolean
  | ((
      value: any,
      isEditing: boolean,
      formData: FormInstance<any>["formData"],
    ) => boolean);

export type PropertyDefinition = {
  id: string;
  label: string;
  accessor?: ValueAccessor;
  help?: string;
  readonly?: PropertyFlag;
  visible?: PropertyFlag;
  required?: PropertyFlag;
  validate?(
    value: any,
    formValues: {
      [key: string]: any;
    },
  ): string | boolean | null | undefined;
  defaultValue?: string | boolean;
  hideLabel?: boolean;
};
export type Property<V = any, FV = V> = PropertyDefinition & {
  displayValue: V;
  formValue: FV;
  hideLabel: boolean;
  readonly: boolean;
  required: boolean;
  visible: boolean;
  setValue: (value: FV | null) => void;
};

export type DataCardSectionInstance<F = any> = {
  isEdited: boolean;
  toggleEdit(): void;
  form: FormInstance<F>;
  setProperty(definition: PropertyDefinition): Property;
  properties: { [key: string]: Property };
};
