import { gql, useQuery } from "@apollo/client";
import Select, {
  SelectOption,
  SelectProps,
} from "core/components/forms/Select";
import { useTranslation } from "next-i18next";
import { useMemo } from "react";
import { DatasourcePickerQuery } from "./DatasourcePicker.generated";

type Option = SelectOption & { symbol?: string; app?: string };

type DatasourcePickerProps = {
  onChange(values: Option[] | null): void;
  value: any;
  className?: string;
} & Omit<
  SelectProps<Option>,
  "onChange" | "options" | "value" | "getOptionLabel"
>;

const DatasourcePicker = (props: DatasourcePickerProps) => {
  const { t } = useTranslation();
  const {
    value,
    onChange,
    placeholder = t("Select datasources"),
    ...delegated
  } = props;

  const { data, loading } = useQuery<DatasourcePickerQuery>(gql`
    query DatasourcePicker {
      catalog(page: 1, perPage: 25) {
        items {
          id
          objectId
          name
          symbol
          type {
            name
            app
          }
        }
      }
    }
  `);

  const options = useMemo(
    () =>
      data?.catalog.items.map((item) => ({
        id: item.objectId,
        symbol: item.symbol,
        label: item.name,
        app: item.type.app,
        type: item.type.name,
      })) ?? [],
    [data]
  );

  const getOptionLabel = (option: Option) => {
    return (
      <div className="flex gap-2">
        {option.symbol && (
          <div className="h-5 w-5 flex-shrink-0">
            <img src={option.symbol} alt="" />
          </div>
        )}
        <span>{option.label}</span>
      </div>
    );
  };
  return (
    <Select<Option>
      {...delegated}
      placeholder={placeholder ?? undefined}
      value={value}
      onChange={onChange}
      options={options}
      getOptionLabel={getOptionLabel}
    />
  );
};

export default DatasourcePicker;
