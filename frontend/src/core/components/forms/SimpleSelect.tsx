import clsx from "clsx";
import { SelectHTMLAttributes, useEffect, useRef } from "react";

export interface SimpleSelectProps
  extends SelectHTMLAttributes<HTMLSelectElement> {
  error?: string | boolean;
  placeholder?: string;
}

const SimpleSelect = (props: SimpleSelectProps) => {
  const {
    className,
    error,
    required,
    children,
    placeholder,
    value,
    multiple,
    ...delegated
  } = props;
  const selectRef = useRef<HTMLSelectElement>(null);

  useEffect(() => {
    if (selectRef.current) {
      selectRef.current.value = `${value ?? ""}`;
    }
  }, [value, selectRef]);

  return (
    <select
      defaultValue={multiple ? [] : ""}
      ref={selectRef}
      multiple={multiple}
      className={clsx(
        "form-select w-full rounded-md border border-gray-300 shadow-xs focus-within:outline-hidden focus:border-blue-500 focus:ring-blue-500  focus-visible:border-blue-500 disabled:cursor-not-allowed sm:text-sm",
        className,
      )}
      required={required}
      {...delegated}
    >
      {placeholder && (
        <option value="" disabled>
          {placeholder}
        </option>
      )}
      {!required && <option></option>}
      {children}
    </select>
  );
};

export default SimpleSelect;
