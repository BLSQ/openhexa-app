import { ParameterField_ParameterFragment } from "./ParameterField.generated";
import { FormInstance } from "core/hooks/useForm";
import { IasoMetadataType } from "graphql/types";
import { gql } from "@apollo/client";
import { useGetConnectionBySlugIasoLazyQuery } from "./IASOWidget.generated";
import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import useIntersectionObserver from "core/hooks/useIntersectionObserver";
import { Combobox, MultiCombobox } from "core/components/forms/Combobox";
import useDebounce from "core/hooks/useDebounce";
import { useTranslation } from "next-i18next";
import { ensureArray } from "core/helpers/array";

type IASOWidgetProps = {
  parameter: ParameterField_ParameterFragment & { connection: string };
  widget: string;
  form: FormInstance<any>;
  workspaceSlug: string;
  name: string;
};

const iasoWidgetToQuery: { [key: string]: IasoMetadataType } = {
  IASO_ORG_UNITS: IasoMetadataType.IasoOrgUnits,
  IASO_PROJECTS: IasoMetadataType.IasoProjects,
  IASO_FORMS: IasoMetadataType.IasoForms,
};

const IASOWidget = ({
  parameter,
  widget,
  form,
  workspaceSlug,
  ...delegated
}: IASOWidgetProps) => {
  const [query, _setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 250);
  const [isLoading, setIsLoading] = useState(false);
  const { t } = useTranslation();
  const [options, setOptions] = useState<any[]>([]);
  const cachedSelectionsRef = useRef<
    Map<string, { id: string; label: string }>
  >(new Map());
  const [fetchData, { data, error }] = useGetConnectionBySlugIasoLazyQuery();
  const hasConnection = useMemo(() => {
    return form.formData[parameter.connection];
  }, [form.formData[parameter.connection]]);

  // Memoize the connection to enforce the IASOConnection type
  const iasoConnection = useMemo(
    () =>
      data?.connectionBySlug?.__typename === "IASOConnection"
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
        type: iasoWidgetToQuery[widget],
        search: debouncedQuery || null,
        filters: [],
        perPage: 15,
        page: resetPagination
          ? 1
          : (iasoConnection?.queryMetadata?.pageNumber || 0) + 1,
      },
    });

    setIsLoading(false);
    if (result.data?.connectionBySlug?.__typename === "IASOConnection") {
      const connection = result.data.connectionBySlug;
      const newOptions = connection.queryMetadata?.items || [];
      setOptions((prevOptions) => {
        if (connection.queryMetadata?.pageNumber === 1) {
          return newOptions;
        }
        return [...prevOptions, ...newOptions];
      });
    }
  };

  const initializeCacheFromForm = () => {
    const ids = ensureArray(form.formData[parameter.code]);
    ids.forEach((id: string) => {
      if (!cachedSelectionsRef.current.has(id)) {
        cachedSelectionsRef.current.set(id, {
          id,
          label: t("Unknown ID: {{id}}", { id }),
        });
      }
    });
  };
  useEffect(() => {
    // Initialize the cache with the current form data
    initializeCacheFromForm();
  }, []);
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
      connection?.__typename !== "IASOConnection" ||
      !connection.queryMetadata
    ) {
      return "";
    }
    const apiError = connection.queryMetadata.error;
    if (apiError) {
      console.error("API Error:", apiError);
      return t("Failed to connect to IASO");
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
        const selectedArray = ensureArray<{ id: string; label: string }>(
          selectedValue,
        );
        selectedArray.forEach((item) => {
          if (item?.id) {
            cachedSelectionsRef.current.set(item.id, item);
          }
        });
        form.setFieldValue(
          parameter.code,
          selectedArray.map((item) => item.id),
        );
      } else {
        if (selectedValue?.id) {
          cachedSelectionsRef.current.set(selectedValue.id, selectedValue);
        }
        form.setFieldValue(parameter.code, selectedValue?.id);
      }
    },
    [form, parameter.code, parameter.multiple],
  );

  const selectedObjects = useMemo(() => {
    const ids = ensureArray(form.formData[parameter.code]);

    const selectObject = (id: string) => {
      return (
        options.find((item) => item.id === id) ||
        cachedSelectionsRef.current.get(id) || {
          id,
          label: t("Unknown ID: {{id}}", { id }),
        }
      );
    };

    if (parameter.multiple) {
      return ids.map(selectObject);
    }

    const singleId = ids[0];
    return singleId ? selectObject(singleId) : null;
  }, [form.formData[parameter.code], options]);

  const onScrollBottom = useCallback(() => {
    if (
      !isLoading &&
      (iasoConnection?.queryMetadata?.totalItems || 0) > options.length
    ) {
      fetchMoreOptions();
    }
  }, [iasoConnection, options, isLoading]);

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

export { IASOWidget, iasoWidgetToQuery };
