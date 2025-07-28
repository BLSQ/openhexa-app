import { gql } from "@apollo/client";
import { useCallback, useState, useEffect } from "react";
import { ComboboxOption } from "@headlessui/react";
import { useTranslation } from "next-i18next";

import useDebounce from "core/hooks/useDebounce";
import { Combobox } from "core/components/forms/Combobox";
import User from "core/features/User";

import {
  useGetUsersQuery,
  UserPicker_UserFragment,
  GetUsersQuery,
} from "./UserPicker.generated";

type UserPickerProps = {
  id?: string;
  workspaceSlug?: string;
  organizationId?: string;
  value: UserPicker_UserFragment | null;
  onChange(user: UserPicker_UserFragment | null): void;
};

const Classes = {
  newUser: "p-2 text-gray-900 hover:bg-blue-500 hover:text-white",
};

export const UserPicker = (props: UserPickerProps) => {
  const { t } = useTranslation();
  const { id, workspaceSlug, value, onChange, organizationId } = props;

  const [query, setQuery] = useState<string>("");
  const [displayData, setDisplayData] = useState<GetUsersQuery | null>(null);

  const debouncedQuery = useDebounce(query, 250);
  const { data, loading } = useGetUsersQuery({
    variables: {
      query: debouncedQuery,
      workspaceSlug: workspaceSlug,
      organizationId: organizationId,
    },
    skip: !debouncedQuery,
  });

  useEffect(() => {
    if (data?.users) {
      setDisplayData(data);
    }
  }, [data]);

  const renderOptions = () => {
    // No query - don't show options
    if (!debouncedQuery) return null;

    // Use cached displayData to prevent flickering during loading
    const users = displayData?.users || [];

    // Show cached user results
    if (users.length > 0) {
      return users.map((user) => (
        <Combobox.CheckOption key={user.id} value={user}>
          <User user={user} subtext />
        </Combobox.CheckOption>
      ));
    }

    // Show invite option when:
    // 1. We have search results but no users found
    // 2. Or we're not loading and have a query (prevents showing during initial load)
    if (displayData || !loading) {
      return (
        <ComboboxOption
          value={{ email: debouncedQuery }}
          className={Classes.newUser}
        >
          {t("Invite new user: ") + debouncedQuery}
        </ComboboxOption>
      );
    }

    // Still loading initial query - don't show anything to prevent flickering
    return null;
  };

  return (
    <Combobox
      id={id}
      required
      onChange={(user) => onChange(user!)}
      loading={loading}
      withPortal={true}
      displayValue={(user) => user?.email ?? ""}
      onInputChange={useCallback(
        (event: any) => setQuery(event.target.value),
        [],
      )}
      placeholder={t("Search users")}
      value={value}
    >
      {renderOptions()}
    </Combobox>
  );
};

UserPicker.fragments = {
  user: gql`
    fragment UserPicker_user on User {
      ...User_user
    }
    ${User.fragments.user}
  `,
};
