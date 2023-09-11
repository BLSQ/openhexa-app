import clsx from "clsx";
import { LabelHTMLAttributes } from "react";

const Label = (props: LabelHTMLAttributes<HTMLLabelElement>) => {
  return (
    <label
      {...props}
      className={clsx(
        "block text-sm font-medium",
        props.color ?? "text-gray-600",
        props.className,
      )}
    />
  );
};

export default Label;
