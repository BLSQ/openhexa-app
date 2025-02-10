import clsx from "clsx";
import { TextareaHTMLAttributes } from "react";

export type TextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & {
  error?: string | null | false | true;
};

const Textarea = (props: TextareaProps) => {
  const { className, error, rows = 4, value, ...delegated } = props;
  return (
    <textarea
      rows={rows}
      className={clsx(
        "form-textarea w-full appearance-none rounded-md border px-3 py-2 focus:z-10 focus:outline-hidden disabled:cursor-not-allowed disabled:opacity-50 sm:text-sm",
        error
          ? "border-red-300  text-red-900  placeholder-red-300  focus:border-red-500  focus:ring-red-500"
          : "border-gray-300 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:ring-blue-500",
        className,
      )}
      value={value}
      {...delegated}
    />
  );
};

export default Textarea;
