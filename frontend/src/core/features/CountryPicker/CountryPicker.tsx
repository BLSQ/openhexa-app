import { gql, useQuery } from "@apollo/client";
import { Combobox, MultiCombobox } from "core/components/forms/Combobox";
import useDebounce from "core/hooks/useDebounce";
import { useTranslation } from "next-i18next";
import { useCallback, useMemo, useState } from "react";
import {
  CountryPickerQuery,
  CountryPickerQueryVariables,
  CountryPicker_CountryFragment,
} from "./CountryPicker.generated";
import Flag from "react-world-flags";

type CountryPickerProps = {
  disabled?: boolean;
  placeholder?: string;
  required?: boolean;
  multiple?: boolean;
  withPortal?: boolean;
  value?: CountryPicker_CountryFragment | CountryPicker_CountryFragment[];
  onChange(
    value?: CountryPicker_CountryFragment | CountryPicker_CountryFragment[],
  ): void;
};

function CountryPicker(props: CountryPickerProps) {
  const { t } = useTranslation();
  const {
    value,
    onChange,
    disabled = false,
    required = false,
    multiple,
    withPortal,
    placeholder = t("Select a country"),
  } = props;

  const { data, loading } = useQuery<
    CountryPickerQuery,
    CountryPickerQueryVariables
  >(
    gql`
      query CountryPicker {
        countries {
          ...CountryPicker_country
        }
      }
      ${CountryPicker.fragments.country}
    `,
    { fetchPolicy: "cache-first" },
  );
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 150);

  const options = useMemo(() => {
    const lowercaseQuery = debouncedQuery.toLowerCase();
    return (
      data?.countries?.filter((c) =>
        c.name.toLowerCase().includes(lowercaseQuery),
      ) ?? []
    );
  }, [data, debouncedQuery]);

  const PickerComponent: any = multiple ? MultiCombobox : Combobox;
  return (
    <PickerComponent
      required={required}
      onChange={onChange}
      loading={loading}
      withPortal={withPortal}
      displayValue={(value: { name: any }) => value?.name ?? ""}
      by="code"
      onInputChange={useCallback(
        (event: any) => setQuery(event.target.value),
        [],
      )}
      placeholder={placeholder}
      value={value as any}
      onClose={useCallback(() => setQuery(""), [])}
      disabled={disabled}
    >
      {options.map((option) => (
        <Combobox.CheckOption key={option.code} value={option}>
          <div className="flex items-center">
            <Flag
              code={option.code}
              className="mr-2 sr-hidden"
              width={16}
              height={11}
            />
            {option.name}
          </div>
        </Combobox.CheckOption>
      ))}
    </PickerComponent>
  );
}

CountryPicker.fragments = {
  country: gql`
    fragment CountryPicker_country on Country {
      code
      alpha3
      name
    }
  `,
};

export default CountryPicker;
