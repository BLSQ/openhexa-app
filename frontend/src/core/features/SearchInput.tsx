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
} & Pick<React.ComponentProps<typeof Input>, "onChange" | "value" | "name">;

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
    return (
      <form onSubmit={onSubmit}>
        <Input
          ref={ref}
          data-testid="search-input"
          leading={<MagnifyingGlassIcon className="h-5 text-gray-500" />}
          autoComplete="off"
          trailingIcon={loading && <Spinner size="xs" />}
          className={className}
          placeholder={placeholder}
          {...delegated}
        />
      </form>
    );
  },
);

export default SearchInput;
