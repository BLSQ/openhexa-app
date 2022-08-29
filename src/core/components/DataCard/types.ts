import { FormInstance } from "core/hooks/useForm";
import { ValueAccessor } from "core/hooks/useItemContext";

export type PropertyFlag = boolean | ((value: any) => boolean);

export type PropertyDefinition = {
  id: string;
  label: string;
  accessor: ValueAccessor;
  readonly?: PropertyFlag;
  visible?: PropertyFlag;
  required?: PropertyFlag;
};
export interface Property<V = any, FV = V> {
  id: string;
  label: string;
  displayValue: V;
  formValue: FV;
  readonly: boolean;
  required: boolean;
  visible: boolean;
  setValue: (value: FV | null) => void;
}

export type DataCardSectionInstance<F = any> = {
  isEdited: boolean;
  toggleEdit(): void;
  form: FormInstance<F>;
  setProperty(definition: PropertyDefinition): Property;
  properties: { [key: string]: Property };
};
