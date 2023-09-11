import { gql, useQuery } from "@apollo/client";
import { useCallback, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import useDebounce from "core/hooks/useDebounce";
import { Combobox, MultiCombobox } from "core/components/forms/Combobox";
import { WorkspaceMemberPickerQuery } from "./WorkspaceMemberPicker.generated";

type Option = {
  id: string;
  user: { id: string; displayName: string };
};

type WorkspaceMemberPickerProps = {
  value: Option | Option[];
  workspaceSlug: string;
  placeholder?: string;
  onChange(value: Option | Option[]): void;
  required?: boolean;
  disabled?: boolean;
  withPortal?: boolean;
};

const WorkspaceMemberPicker = (props: WorkspaceMemberPickerProps) => {
  const { t } = useTranslation();
  const {
    workspaceSlug,
    value,
    disabled = false,
    required = false,
    withPortal = false,
    onChange,
    placeholder = t("Select recipients"),
  } = props;

  const { data, loading } = useQuery<WorkspaceMemberPickerQuery>(
    gql`
      query WorkspaceMemberPicker($slug: String!) {
        workspace(slug: $slug) {
          slug
          ...WorkspaceMemberPicker_workspace
        }
      }
      ${WorkspaceMemberPicker.fragments.workspace}
    `,
    { variables: { slug: workspaceSlug } },
  );
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 150);

  const options = useMemo(() => {
    const lowercaseQuery = debouncedQuery.toLowerCase();
    return (
      data?.workspace?.members.items?.filter((c) =>
        c.user.displayName.toLowerCase().includes(lowercaseQuery),
      ) ?? []
    );
  }, [data, debouncedQuery]);

  const displayValue = useCallback(
    (option: Option) => (option ? option.user.displayName : ""),
    [],
  );

  return (
    <MultiCombobox
      required={required}
      onChange={onChange}
      loading={loading}
      withPortal={withPortal}
      displayValue={displayValue}
      by={(a: Option, b: Option) => a.user.id === b.user.id}
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
        <Combobox.CheckOption key={option.user.id} value={option}>
          {option.user.displayName}
        </Combobox.CheckOption>
      ))}
    </MultiCombobox>
  );
};

WorkspaceMemberPicker.fragments = {
  workspace: gql`
    fragment WorkspaceMemberPicker_workspace on Workspace {
      slug
      members {
        items {
          id
          user {
            id
            displayName
          }
        }
      }
    }
  `,
};

export default WorkspaceMemberPicker;
