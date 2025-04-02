import { InputHTMLAttributes, forwardRef, ReactNode } from "react";
import clsx from "clsx";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: string | null | false | true;
  trailingIcon?: ReactNode;
  leading?: ReactNode;
  fullWidth?: boolean;
}

const Input = forwardRef<HTMLInputElement, InputProps>((props, ref) => {
  const {
    type,
    name,
    error,
    defaultValue,
    className,
    trailingIcon,
    leading = null,
    value,
    fullWidth = false,
    ...delegated
  } = props;

  const inputClassName = clsx(
    "form-input appearance-none relative block",
    "px-3 py-2 border rounded-md focus:outline-hidden focus:z-10 sm:text-sm",
    "disabled:opacity-50 disabled:cursor-not-allowed",
    error
      ? "border-red-300 placeholder-red-300  text-red-900  focus:ring-red-500  focus:border-red-500"
      : "border-gray-300 placeholder-gray-500 text-gray-900 focus:ring-blue-500 focus:border-blue-500",
    trailingIcon && "pr-4",
    leading && "pl-10",
    fullWidth && "w-full",
    className,
  );

  return (
    <div className={clsx("group relative", fullWidth && "w-full")}>
      <input
        id={name}
        name={name}
        type={type ?? "text"}
        aria-invalid={Boolean(error)}
        aria-describedby={`${name}-description`}
        className={inputClassName}
        value={defaultValue ? undefined : (value ?? "")}
        defaultValue={defaultValue}
        {...delegated}
        ref={ref}
      />
      {leading && (
        <div className="absolute inset-y-0 left-0 z-30 inline-flex items-center justify-center pl-2.5">
          {leading}
        </div>
      )}
      {trailingIcon && (
        <div className="absolute inset-y-0 right-0 z-10 inline-flex items-center justify-center pr-2.5">
          {trailingIcon}
        </div>
      )}
    </div>
  );
});

Input.displayName = "Input";

export default Input;
