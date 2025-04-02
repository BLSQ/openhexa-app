import { gql } from "@apollo/client";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslation } from "next-i18next";
import { Combobox, MultiCombobox } from "core/components/forms/Combobox";
import useDebounce from "core/hooks/useDebounce";
import { useGetConnectionBySlugLazyQuery } from "./DHIS2Widget.generated";
import { ParameterField_ParameterFragment } from "./ParameterField.generated";
import useIntersectionObserver from "core/hooks/useIntersectionObserver";
import { FormInstance } from "core/hooks/useForm";
import { Dhis2MetadataType } from "graphql/types";
import { ensureArray } from "core/helpers/array";

type DHIS2WidgetProps = {
  parameter: ParameterField_ParameterFragment & { connection: string };
  widget: string;
  form: FormInstance<any>;
  workspaceSlug: string;
  name: string;
};

export const GET_CONNECTION_METADATA = gql`
  query getConnectionBySlug(
    $workspaceSlug: String!
    $connectionSlug: String!
    $type: DHIS2MetadataType!
    $filters: [String!]
    $perPage: Int
    $page: Int
  ) {
    connectionBySlug(
      workspaceSlug: $workspaceSlug
      connectionSlug: $connectionSlug
    ) {
      ... on DHIS2Connection {
        queryMetadata(
          type: $type
          filters: $filters
          perPage: $perPage
          page: $page
        ) {
          items {
            id
            label
          }
          pageNumber
          totalItems
          error
        }
      }
    }
  }
`;

const dhis2WidgetToQuery: { [key: string]: Dhis2MetadataType } = {
  DHIS2_ORG_UNITS: Dhis2MetadataType.OrgUnits,
  DHIS2_ORG_UNIT_GROUPS: Dhis2MetadataType.OrgUnitGroups,
  DHIS2_ORG_UNIT_LEVELS: Dhis2MetadataType.OrgUnitLevels,
  DHIS2_DATASET: Dhis2MetadataType.OrgUnitLevels,
  DHIS2_DATA_ELEMENTS: Dhis2MetadataType.DataElements,
  DHIS2_DATA_ELEMENT_GROUPS: Dhis2MetadataType.DataElementGroups,
  DHIS2_INDICATORS: Dhis2MetadataType.Indicators,
  DHIS2_INDICATOR_GROUPS: Dhis2MetadataType.IndicatorGroups,
};

const DHIS2Widget = ({
  parameter,
  widget,
  form,
  workspaceSlug,
  ...delegated
}: DHIS2WidgetProps) => {
  const [query, _setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 250);
  const [isLoading, setIsLoading] = useState(false);
  const { t } = useTranslation();
  const [options, setOptions] = useState<any[]>([]);
  const [fetchData, { data, error }] = useGetConnectionBySlugLazyQuery();
  const hasConnection = useMemo(() => {
    return form.formData[parameter.connection];
  }, [form.formData[parameter.connection]]);

  // Memoize the connection to enforce the DHIS2Connection type
  const dhis2Connection = useMemo(
    () =>
      data?.connectionBySlug?.__typename === "DHIS2Connection"
        ? data.connectionBySlug
        : null,
    [data?.connectionBySlug],
  );

  const setQuery = useCallback((newQuery: string) => {
    if (newQuery === debouncedQuery) return;
    _setQuery(newQuery);
  }, []);

  const fetchMoreOptions = async (resetPagination: boolean = false) => {
    setIsLoading(true);
    const result = await fetchData({
      variables: {
        workspaceSlug,
        connectionSlug: form.formData[parameter.connection],
        type: dhis2WidgetToQuery[widget],
        filters: debouncedQuery ? ["name:token:" + debouncedQuery] : [],
        perPage: 15,
        page: resetPagination
          ? 1
          : (dhis2Connection?.queryMetadata?.pageNumber || 0) + 1,
      },
    });
    setIsLoading(false);
    if (result.data?.connectionBySlug?.__typename === "DHIS2Connection") {
      const connection = result.data.connectionBySlug;
      const newOptions = connection.queryMetadata?.items || [];
      setOptions((prevOptions) => {
        // If it's the first page, replace options
        if (connection.queryMetadata?.pageNumber === 1) {
          return newOptions;
        }
        // Otherwise append to existing options
        return [...prevOptions, ...newOptions];
      });
    }
  };

  // Initial load & when connection changes
  useEffect(() => {
    if (!hasConnection) return;
    fetchMoreOptions(true);
  }, [hasConnection, debouncedQuery]);

  const errorMessage = useMemo(() => {
    if (error) {
      console.error("GraphQL Error:", error);
      return error.message || t("An unexpected error occurred.");
    }
    const connection = data?.connectionBySlug;
    if (
      connection?.__typename !== "DHIS2Connection" ||
      !connection.queryMetadata
    ) {
      return "";
    }
    const apiError = connection.queryMetadata.error;
    if (apiError) {
      console.error("API Error:", apiError);
      return t("Failed connect to DHIS2");
    }

    return "";
  }, [error, data, t]);

  const displayValueHandler = (value: any) => {
    if (!value) return "";

    const getLabel = (item: any) => {
      if (typeof item === "object" && item !== null) return item.label;
      const foundItem = options.find((opt) => opt.id === item);
      return foundItem?.label ?? t("Unknown ID: {{id}}", { id: item });
    };

    if (Array.isArray(value)) {
      return value.map(getLabel).filter(Boolean).join(", ");
    }

    return getLabel(value);
  };

  const handleSelectionChange = useCallback(
    (selectedValue: any) => {
      if (parameter.multiple) {
        form.setFieldValue(
          parameter.code,
          ensureArray<{ id: string; label: string }>(selectedValue).map(
            (item) => item.id,
          ),
        );
      } else {
        form.setFieldValue(parameter.code, selectedValue?.id);
      }
    },
    [form, parameter.code, parameter.multiple],
  );

  const selectedObjects = useMemo(() => {
    if (!form.formData[parameter.code]) return parameter.multiple ? [] : null;

    if (Array.isArray(form.formData[parameter.code])) {
      return form.formData[parameter.code].map(
        (id: string) =>
          options.find((item) => item.id === id) || {
            id,
            label: t("Unknown ID: {{id}}", { id }),
          },
      );
    }

    return (
      options.find((item) => item.id === form.formData[parameter.code]) || {
        id: form.formData[parameter.code],
        label: t("Unknown ID: {{id}}", { id: form.formData[parameter.code] }),
      }
    );
  }, [form.formData[parameter.code], options]);

  const onScrollBottom = useCallback(() => {
    if (
      !isLoading &&
      (dhis2Connection?.queryMetadata?.totalItems || 0) > options.length
    ) {
      fetchMoreOptions();
    }
  }, [dhis2Connection, options, isLoading]);

  const PickerComponent = parameter.multiple ? MultiCombobox : Combobox;

  return (
    <PickerComponent
      onChange={handleSelectionChange}
      loading={isLoading}
      displayValue={displayValueHandler}
      by="id"
      onInputChange={(e) => setQuery(e.target.value)}
      placeholder={t("Select options")}
      value={selectedObjects}
      disabled={!hasConnection}
      withPortal
      onClose={useCallback(() => setQuery(""), [])}
      error={errorMessage}
      {...delegated}
    >
      {options.map((option) => (
        <Combobox.CheckOption key={option.id} value={option}>
          {option.label}
        </Combobox.CheckOption>
      ))}
      {onScrollBottom && (
        <IntersectionObserverWrapper onScrollBottom={onScrollBottom} />
      )}
    </PickerComponent>
  );
};
const IntersectionObserverWrapper = ({
  onScrollBottom,
}: {
  onScrollBottom: () => void;
}) => {
  const [lastElement, setLastElement] = useState<Element | null>(null);
  const list = useIntersectionObserver(lastElement, {});

  useEffect(() => {
    if (lastElement && list?.isIntersecting) {
      onScrollBottom();
    }
  }, [onScrollBottom, list, lastElement]);

  return <div ref={setLastElement}></div>;
};

export { DHIS2Widget, dhis2WidgetToQuery };
