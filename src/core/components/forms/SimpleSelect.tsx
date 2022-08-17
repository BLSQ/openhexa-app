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
      defaultValue={""}
      ref={selectRef}
      className={clsx(
        "form-select rounded-md border-gray-300 shadow-sm sm:text-sm",
        "hover:border-gray-400 focus:border-gray-300 focus:outline-none focus:ring-transparent",
        "disabled:cursor-not-allowed disabled:border-gray-300 disabled:bg-gray-50",
        "placeholder-gray-600 placeholder-opacity-70",
        error &&
          "border-red-300 text-red-900 placeholder-red-300 focus:border-red-300 focus:ring-red-500",
        className
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
