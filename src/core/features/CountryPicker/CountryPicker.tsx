import { gql, useQuery } from "@apollo/client";
import Combobox from "core/components/forms/Combobox";
import { ensureArray } from "core/helpers/array";
import useDebounce from "core/hooks/useDebounce";
import { useTranslation } from "next-i18next";
import { useCallback, useMemo, useState } from "react";
import {
  CountryPickerQuery,
  CountryPickerQueryVariables,
  CountryPicker_CountryFragment,
} from "./CountryPicker.generated";

type CountryPickerProps = {
  disabled?: boolean;
  placeholder?: string;
  required?: boolean;
  withPortal?: boolean;
  multiple?: boolean;
  value: CountryPicker_CountryFragment | CountryPicker_CountryFragment[] | null;
  onChange: (
    value:
      | CountryPicker_CountryFragment
      | CountryPicker_CountryFragment[]
      | null
  ) => void;
};

const CountryPicker = (props: CountryPickerProps) => {
  const { t } = useTranslation();
  const {
    value,
    onChange,
    disabled = false,
    multiple = false,
    required = false,
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
    { fetchPolicy: "cache-first" }
  );
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 150);

  const options = useMemo(() => {
    const lowercaseQuery = debouncedQuery.toLowerCase();
    return (
      data?.countries?.filter((c) =>
        c.name.toLowerCase().includes(lowercaseQuery)
      ) ?? []
    );
  }, [data, debouncedQuery]);

  return (
    <Combobox<CountryPicker_CountryFragment>
      required={required}
      onChange={onChange}
      loading={loading}
      withPortal={withPortal}
      displayValue={(value) =>
        value
          ? ensureArray(value)
              .map((v) => v.name)
              .join(", ")
          : ""
      }
      by="code" /* FIXME: Upgrade @headlessui/react to > 1.6.6 to fix the comparison criteria */
      onInputChange={useCallback((event) => setQuery(event.target.value), [])}
      placeholder={placeholder}
      value={value}
      multiple={multiple}
      onClose={useCallback(() => setQuery(""), [])}
      disabled={disabled}
    >
      {options.map((option) => (
        <Combobox.CheckOption key={option.code} value={option}>
          <div className="flex items-center">
            <img
              loading="lazy"
              src={option.flag}
              className="sr-hidden mr-2"
              width={16}
              height={11}
              alt="Country Flag"
            />
            {option.name}
          </div>
        </Combobox.CheckOption>
      ))}
    </Combobox>
  );
};

CountryPicker.fragments = {
  country: gql`
    fragment CountryPicker_country on Country {
      code
      alpha3
      name
      flag
    }
  `,
};

export default CountryPicker;
