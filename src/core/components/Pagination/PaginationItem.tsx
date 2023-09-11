import clsx from "clsx";
import { ReactElement } from "react";

type PaginationItemProps = {
  children: ReactElement | string | ReactElement[];
  current?: boolean;
  disabled?: boolean;
  onClick?: () => void;
};

const PaginationItem = (props: PaginationItemProps) => {
  const { children, current, onClick, disabled = false } = props;
  return (
    <button
      onClick={onClick}
      aria-current="page"
      type="button"
      disabled={disabled}
      className={clsx(
        "relative inline-flex cursor-pointer items-center border border-gray-300 bg-white px-3 py-1 text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50",
        current && "border-who-blue-main text-who-blue-main z-10 bg-indigo-50",
        "first:rounded-bl-md first:rounded-tl-md last:rounded-br-md last:rounded-tr-md",
      )}
    >
      {children}
    </button>
  );
};

export default PaginationItem;
