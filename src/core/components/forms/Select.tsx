import { ChangeEventHandler, ReactNode, useMemo, useState } from "react";
import Combobox, { ComboboxProps } from "./Combobox/Combobox";

export type SelectOption = {
  label: string;
  id: string;
};

export type SelectProps<O extends SelectOption> = {
  options: O[];
  value: O | O[] | null;
  onChange(value: O | O[] | null): void;
  getOptionLabel?(option: O): ReactNode | string;
} & Pick<
  ComboboxProps,
  "placeholder" | "disabled" | "multiple" | "name" | "required" | "className"
>;

function Select<O extends SelectOption>(props: SelectProps<O>) {
  const {
    options,
    value,
    onChange,
    multiple,
    disabled,
    placeholder,
    className,
    name,
    getOptionLabel = (o) => o.label,
    required,
  } = props;
  const [query, setQuery] = useState<string | null>(null);

  const onInputChange: ChangeEventHandler<HTMLInputElement> = (event) => {
    setQuery(event.target.value);
  };

  const filteredOptions = useMemo(
    () =>
      !query
        ? options
        : options.filter((opt) =>
            opt.label.toLowerCase().includes(query.toLowerCase())
          ),
    [options, query]
  );

  return (
    <Combobox
      value={value}
      name={name}
      required={required}
      multiple={multiple}
      placeholder={placeholder}
      disabled={disabled}
      onInputChange={onInputChange}
      className={className}
      onChange={onChange}
      displayValue={(v) => v.label}
      withPortal
    >
      {filteredOptions.map((option, i) => (
        <Combobox.CheckOption key={i} value={option}>
          {getOptionLabel(option)}
        </Combobox.CheckOption>
      ))}
    </Combobox>
  );
}

export default Select;
