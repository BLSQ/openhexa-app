import { MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import Input from "core/components/forms/Input";
import Spinner from "core/components/Spinner";
import { useTranslation } from "next-i18next";
import { forwardRef } from "react";

type SearchInputProps = {
  loading?: boolean;
  placeholder?: string;
  className?: string;
  onSubmit?: React.FormEventHandler<HTMLFormElement>;
  required?: boolean;
} & Pick<
  React.ComponentProps<typeof Input>,
  "onChange" | "value" | "name" | "fitWidth" | "fullWidth"
>;

const SearchInput = forwardRef<HTMLInputElement, SearchInputProps>(
  (props, ref) => {
    const { t } = useTranslation();
    const {
      className,
      loading,
      placeholder = t("Search..."),
      onSubmit,
      ...delegated
    } = props;
    const content = (
      <Input
        ref={ref}
        data-testid="search-input"
        leading={<MagnifyingGlassIcon className="h-5 text-gray-500" />}
        autoComplete="off"
        trailingIcon={loading && <Spinner size="xs" />}
        className={className}
        iconZIndex="z-0"
        placeholder={placeholder}
        {...delegated}
      />
    );

    return onSubmit ? <form onSubmit={onSubmit}>{content}</form> : content;
  },
);

export default SearchInput;
