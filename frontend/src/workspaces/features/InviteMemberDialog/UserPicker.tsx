import { useCallback, useState } from "react";
import { ComboboxOption } from "@headlessui/react";
import clsx from "clsx";
import { useTranslation } from "next-i18next";

import UserComponent from "core/features/User";
import useDebounce from "core/hooks/useDebounce";
import { Combobox } from "core/components/forms/Combobox";
import { useGetUsersQuery } from "identity/graphql/queries.generated";

type UserPickerProps = {
  workspaceSlug: string;
  form: any;
};

const Classes = {
  newUser: "p-2 text-gray-900 hover:bg-blue-500 hover:text-white",
};

export const UserPicker = (props: UserPickerProps) => {
  const { t } = useTranslation();
  const { workspaceSlug, form } = props;

  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 250);
  const { data, loading } = useGetUsersQuery({
    variables: {
      query: debouncedQuery,
      workspaceSlug: workspaceSlug,
    },
  });

  return (
    <Combobox
      required
      onChange={(user) => form.setFieldValue("user", user)}
      loading={loading}
      withPortal={true}
      displayValue={(user) => user?.email ?? ""}
      onInputChange={useCallback(
        (event: any) => setQuery(event.target.value),
        [],
      )}
      placeholder={t("Search users")}
      value={form.formData.user}
      onClose={useCallback(() => setQuery(""), [])}
    >
      <ComboboxOption
        value={{ email: query }}
        className={clsx(!data?.users.length && Classes.newUser)}
      >
        {!data?.users.length && t("Invite new user: ") + query}
      </ComboboxOption>
      {data?.users.map((user) => (
        <Combobox.CheckOption key={user.id} value={user}>
          {user.email} ({user.displayName}){/* <UserComponent user=user /> */}
        </Combobox.CheckOption>
      ))}
    </Combobox>
  );
};
