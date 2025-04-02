import Label from "../Label";
import { ReactElement, ReactNode } from "react";
import Input from "../Input";
import clsx from "clsx";
import Tooltip from "core/components/Tooltip";
import { InformationCircleIcon } from "@heroicons/react/20/solid";

interface CommonProps {
  label?: string;
  error?: string | null | false;
  required?: boolean;
  description?: ReactNode | string;
  showOptional?: boolean;
  name: string;
  help?: ReactNode;
  className?: string;
  labelColor?: string;
  errorColor?: string;
}

type CustomField = CommonProps & {
  children: ReactElement | ReactElement[];
};

type InputField = CommonProps & React.ComponentProps<typeof Input>;

const Field = (props: CustomField | InputField) => {
  const {
    error,
    description,
    label,
    required,
    name,
    help,
    showOptional = true,
    className,
    labelColor,
    errorColor = "text-red-600",
    ...delegated
  } = props;

  let children;
  if (props.children) {
    children = props.children;
  } else {
    children = (
      <Input name={name} error={error} required={required} {...delegated} />
    );
  }

  return (
    <div className={className}>
      {label && (
        <div className="mb-1 flex justify-between">
          <Label htmlFor={name} className={clsx("flex", labelColor)}>
            {label}
            {help && (
              <Tooltip
                placement="top"
                renderTrigger={(ref) => (
                  <span ref={ref} data-testid="help">
                    <InformationCircleIcon className="ml-1 h-3 w-3 cursor-pointer" />
                  </span>
                )}
                label={help}
              />
            )}
          </Label>
          {!required && showOptional && (
            <span className="text-sm text-gray-400">Optional</span>
          )}
        </div>
      )}
      {children}
      {description && (
        <p className="mt-2 text-sm text-gray-500">{description}</p>
      )}
      {error && <p className={clsx("mt-2 text-sm", errorColor)}>{error}</p>}
    </div>
  );
};

export default Field;
