import { gql, useQuery } from "@apollo/client";
import { useCallback, useMemo, useState } from "react";
import { useTranslation } from "next-i18next";
import useDebounce from "core/hooks/useDebounce";
import { Combobox } from "core/components/forms/Combobox";
import { ConnectionType } from "graphql/types";
import Connections from "workspaces/helpers/connections";
import { WorkspaceConnectionPickerQuery } from "./WorkspaceConnectionPicker.generated";

type Option = {
  id: string;
  slug: string;
  name: string;
  type: ConnectionType;
};

type WorkspaceConnectionPickerProps = {
  value?: string;
  workspaceSlug: string;
  placeholder?: string;
  onChange(value?: Option): void;
  required?: boolean;
  disabled?: boolean;
  withPortal?: boolean;
  type?: ConnectionType;
};

const WorkspaceConnectionPicker = (props: WorkspaceConnectionPickerProps) => {
  const { t } = useTranslation();
  const {
    workspaceSlug,
    value,
    disabled = false,
    required = false,
    withPortal = false,
    onChange,
    placeholder = t("Select connection"),
    type,
  } = props;

  const { data, loading } = useQuery<WorkspaceConnectionPickerQuery>(
    gql`
      query WorkspaceConnectionPicker($slug: String!) {
        workspace(slug: $slug) {
          slug
          ...WorkspaceConnectionPicker_workspace
        }
      }
      ${WorkspaceConnectionPicker.fragments.workspace}
    `,
    { variables: { slug: workspaceSlug } },
  );

  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 150);

  const options = useMemo(() => {
    const lowercaseQuery = debouncedQuery.toLowerCase();
    return (
      data?.workspace?.connections?.filter((c) => {
        if (type) {
          return (
            c.name.toLowerCase().includes(lowercaseQuery) &&
            c.type.toLowerCase() === type.toLowerCase()
          );
        }
        return c.name.toLowerCase().includes(lowercaseQuery);
      }) ?? []
    );
  }, [data, debouncedQuery, type]);

  const displayValue = useCallback(
    (option: Option) => (option ? option.name : ""),
    [],
  );

  const comboBoxValue = useMemo(() => {
    return options.find((option) => option.slug === value) ?? null;
  }, [value, options]);

  return (
    <Combobox
      required={required}
      onChange={onChange}
      loading={loading}
      withPortal={withPortal}
      displayValue={displayValue}
      by="slug"
      onInputChange={useCallback(
        (event: any) => setQuery(event.target.value),
        [],
      )}
      placeholder={placeholder}
      value={comboBoxValue as any}
      onClose={useCallback(() => setQuery(""), [])}
      disabled={disabled}
    >
      {options.map((option: Option) => (
        <Combobox.CheckOption key={option.id} value={option}>
          <div className="flex items-center">
            <img
              loading="lazy"
              src={Connections[option.type as keyof typeof Connections].iconSrc}
              className="sr-hidden mr-2"
              width={16}
              height={11}
              alt="Connection logo"
            />
            {option.name}
          </div>
        </Combobox.CheckOption>
      ))}
    </Combobox>
  );
};

WorkspaceConnectionPicker.fragments = {
  workspace: gql`
    fragment WorkspaceConnectionPicker_workspace on Workspace {
      slug
      connections {
        id
        name
        slug
        type
      }
    }
  `,
};

export default WorkspaceConnectionPicker;
