import { ChangeEventHandler, ReactNode, useMemo, useState } from "react";
import MultiCombobox from "./Combobox/MultiCombobox";
import Combobox, { ComboboxProps } from "./Combobox/Combobox";

export type SelectOption = { [key: string]: any };

export type SelectProps<O extends SelectOption> = {
  options: O[];
  value: O | O[] | null;
  onChange(value: O | O[] | null): void;
  getOptionLabel(option: SelectOption): ReactNode | string;
  filterOptions?: (options: O[], query: string) => O[];
  displayValue?: (option: O) => string;
  multiple?: boolean;
} & Pick<
  ComboboxProps<O>,
  "placeholder" | "disabled" | "name" | "required" | "className" | "by"
>;

const DEFAULT_FILTER_OPTIONS = (options: SelectOption[], query: string) => {
  return options.filter((opt) =>
    opt.label.toLowerCase().includes(query.toLowerCase())
  );
};

function Select<O extends SelectOption = { [key: string]: any }>(
  props: SelectProps<O>
) {
  const {
    options,
    value,
    onChange,
    multiple,
    disabled,
    placeholder,
    className,
    name,
    by,
    displayValue = (o) => o.label,
    filterOptions = DEFAULT_FILTER_OPTIONS,
    getOptionLabel,
    required,
  } = props;
  const [query, setQuery] = useState<string | null>(null);

  const onInputChange: ChangeEventHandler<HTMLInputElement> = (event) => {
    setQuery(event.target.value);
  };

  const filteredOptions = useMemo(
    () => (!query ? options : filterOptions(options, query)),
    [options, query, filterOptions]
  );

  const Picker = multiple ? MultiCombobox : Combobox;

  return (
    <Picker
      value={value as any}
      name={name}
      required={required}
      placeholder={placeholder}
      disabled={disabled}
      onInputChange={onInputChange}
      className={className}
      onChange={onChange}
      displayValue={displayValue}
      by={by}
      withPortal
    >
      {filteredOptions.map((option, i) => (
        <Combobox.CheckOption key={i} value={option}>
          {getOptionLabel(option)}
        </Combobox.CheckOption>
      ))}
    </Picker>
  );
}

export default Select;
