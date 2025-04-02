import { gql, useLazyQuery } from "@apollo/client";
import { useCallback, useMemo, useState } from "react";
import { useTranslation } from "next-i18next";
import useDebounce from "core/hooks/useDebounce";
import { Combobox, MultiCombobox } from "core/components/forms/Combobox";
import {
  WorkspaceMemberPickerQuery,
  WorkspaceMemberPickerQueryVariables,
} from "./WorkspaceMemberPicker.generated";

export type WorkspaceMemberOption = {
  id: string;
  user: { id: string; displayName: string };
};

type WorkspaceMemberPickerProps = {
  value?: WorkspaceMemberOption | WorkspaceMemberOption[] | null;
  workspaceSlug: string;
  placeholder?: string;
  onChange(value: WorkspaceMemberOption | WorkspaceMemberOption[]): void;
  required?: boolean;
  disabled?: boolean;
  withPortal?: boolean;
  multiple?: boolean;
  exclude?: string[];
};

const WorkspaceMemberPicker = (props: WorkspaceMemberPickerProps) => {
  const { t } = useTranslation();
  const {
    workspaceSlug,
    value,
    disabled = false,
    required = false,
    withPortal = false,
    multiple = false,
    onChange,
    exclude = [],
    placeholder = t("Select member"),
  } = props;

  const [fetch, { data, loading }] = useLazyQuery<
    WorkspaceMemberPickerQuery,
    WorkspaceMemberPickerQueryVariables
  >(gql`
    query WorkspaceMemberPicker($slug: String!) {
      workspace(slug: $slug) {
        slug
        ...WorkspaceMemberPicker_workspace
      }
    }
    ${WorkspaceMemberPicker.fragments.workspace}
  `);

  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 150);

  const options = useMemo(() => {
    const lowercaseQuery = debouncedQuery.toLowerCase();
    return (
      data?.workspace?.members.items?.filter(
        (m) =>
          m.user.displayName.toLowerCase().includes(lowercaseQuery) &&
          !exclude.includes(m.user.id),
      ) ?? []
    );
  }, [data, debouncedQuery, exclude]);

  const displayValue = useCallback(
    (option: WorkspaceMemberOption) => (option ? option.user.displayName : ""),
    [],
  );

  const onInputChange = useCallback(
    (event: any) => setQuery(event.target.value),
    [],
  );

  const onOpen = useCallback(() => {
    fetch({ variables: { slug: workspaceSlug } });
  }, [fetch, workspaceSlug]);

  const onClose = useCallback(() => setQuery(""), []);

  const Picker: any = multiple ? MultiCombobox : Combobox;

  return (
    <Picker
      required={required}
      onChange={onChange}
      loading={loading}
      withPortal={withPortal}
      displayValue={displayValue}
      by={(a: WorkspaceMemberOption, b: WorkspaceMemberOption) =>
        a?.user?.id === b?.user?.id
      }
      onInputChange={onInputChange}
      placeholder={placeholder}
      value={value as any}
      onClose={onClose}
      onOpen={onOpen}
      disabled={disabled}
    >
      {options.map((option) => (
        <Combobox.CheckOption key={option.user.id} value={option}>
          {option.user.displayName}
        </Combobox.CheckOption>
      ))}
    </Picker>
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
