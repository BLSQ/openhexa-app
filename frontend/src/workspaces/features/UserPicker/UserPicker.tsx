import { gql } from "@apollo/client";
import { useCallback, useState, useEffect } from "react";
import { ComboboxOption } from "@headlessui/react";
import clsx from "clsx";
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
  workspaceSlug: string;
  value: UserPicker_UserFragment | null;
  onChange(user: UserPicker_UserFragment | null): void;
};

const Classes = {
  newUser: "p-2 text-gray-900 hover:bg-blue-500 hover:text-white",
};

export const UserPicker = (props: UserPickerProps) => {
  const { t } = useTranslation();
  const { workspaceSlug, value, onChange } = props;

  const [query, setQuery] = useState<string>("");
  const [displayData, setDisplayData] = useState<GetUsersQuery | null>(null);

  const debouncedQuery = useDebounce(query, 250);
  const { data, loading } = useGetUsersQuery({
    variables: {
      query: debouncedQuery,
      workspaceSlug: workspaceSlug,
    },
  });

  useEffect(() => {
    if (data?.users) {
      setDisplayData(data);
    }
  }, [data]);

  return (
    <Combobox
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
      onClose={useCallback(() => setQuery(""), [])}
    >
      <ComboboxOption
        value={{ email: query }}
        className={clsx(!displayData?.users.length && Classes.newUser)}
      >
        {displayData?.users &&
          !displayData?.users.length &&
          t("Invite new user: ") + query}
      </ComboboxOption>
      {displayData?.users.map((user) => (
        <Combobox.CheckOption key={user.id} value={user}>
          <User user={user} subtext />
        </Combobox.CheckOption>
      ))}
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
