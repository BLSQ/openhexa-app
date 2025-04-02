import {
  ChangeEventHandler,
  MouseEventHandler,
  ReactNode,
  useMemo,
  useState,
} from "react";
import MultiCombobox from "./Combobox/MultiCombobox";
import Combobox, { ComboboxProps } from "./Combobox/Combobox";

export type SelectOption = any;

export type SelectProps<O> = {
  options: O[];
  value: O | O[] | null;
  onChange(value: O | O[] | null): void;
  getOptionLabel(option: O): ReactNode | string;
  filterOptions?: (options: O[], query: string) => O[];
  displayValue?: (option: O) => string;
  multiple?: boolean;
  addLabel?: string;
  onCreate?: (query: string) => void;
} & Pick<
  ComboboxProps<O>,
  | "placeholder"
  | "disabled"
  | "name"
  | "required"
  | "className"
  | "by"
  | "loading"
>;

const DEFAULT_FILTER_OPTIONS = (options: SelectOption[], query: string) => {
  return options.filter((opt) =>
    opt.toLowerCase().includes(query.toLowerCase()),
  );
};

function Select<O>(props: SelectProps<O>) {
  const {
    options,
    value,
    onChange,
    onCreate,
    addLabel = "Add",
    multiple,
    disabled,
    placeholder,
    className,
    name,
    by,
    displayValue = (o) => o,
    filterOptions = DEFAULT_FILTER_OPTIONS,
    getOptionLabel,
    required,
    loading,
  } = props;
  const [query, setQuery] = useState<string>("");
  const [__resetKey__, setResetKey] = useState("");

  const onInputChange: ChangeEventHandler<HTMLInputElement> = (event) => {
    setQuery(event.target.value ?? "");
  };

  const filteredOptions = useMemo(
    () => (!query ? options : filterOptions(options, query)),
    [options, query, filterOptions],
  );

  const handleCreate: MouseEventHandler<HTMLDivElement> = (event) => {
    if (!onCreate) return;
    setQuery("");
    setResetKey(Math.random().toString(36).substring(7));
    onCreate(query);
  };

  const Picker = multiple ? MultiCombobox : Combobox;

  return (
    <Picker
      key={__resetKey__}
      value={value as any}
      name={name}
      required={required}
      placeholder={placeholder}
      disabled={disabled}
      onInputChange={onInputChange}
      className={className}
      onChange={onChange}
      displayValue={displayValue as any}
      by={by as any /* Otherwise typescript is not happy */}
      loading={loading}
      withPortal
    >
      {onCreate && query.length > 0 && (
        <div
          className="cursor-pointer p-2 text-gray-900 hover:bg-blue-500 hover:text-white"
          onClick={handleCreate}
        >
          {addLabel} &quot;{query}&quot;
        </div>
      )}
      {filteredOptions.map((option, i) => (
        <Combobox.CheckOption key={i} value={option}>
          {getOptionLabel(option)}
        </Combobox.CheckOption>
      ))}
    </Picker>
  );
}

export default Select;
