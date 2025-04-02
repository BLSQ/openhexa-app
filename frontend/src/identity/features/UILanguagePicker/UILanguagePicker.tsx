import SimpleSelect from "core/components/forms/SimpleSelect";
import { LANGUAGES } from "core/helpers/i18n";
import { useUpdateUserMutation } from "identity/graphql/mutations.generated";
import useMe from "identity/hooks/useMe";
import { useRouter } from "next/router";

const UILanguagePicker = ({ className }: { className?: string }) => {
  const me = useMe();
  const router = useRouter();
  const [updateUser] = useUpdateUserMutation();
  if (!me?.user?.language) {
    return null;
  }

  const onLangChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const prevLang = me.user!.language;
    updateUser({
      variables: { input: { language: e.target.value as "en" | "fr" } },
    });
    if (prevLang !== e.target.value) {
      router.replace("/");
    }
  };
  return (
    <SimpleSelect
      className={className}
      value={me.user.language}
      required
      onChange={onLangChange}
    >
      {Object.entries(LANGUAGES).map(([key, value]) => (
        <option key={key} value={key}>
          {value}
        </option>
      ))}
    </SimpleSelect>
  );
};

export default UILanguagePicker;
