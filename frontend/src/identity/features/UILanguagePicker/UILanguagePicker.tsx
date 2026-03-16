import SimpleSelect from "core/components/forms/SimpleSelect";
import { LANGUAGES } from "core/helpers/i18n";
import { useUpdateUserMutation } from "identity/graphql/mutations.generated";
import useMe from "identity/hooks/useMe";
import { useRouter } from "next/router";

type UILanguagePickerProps = {
  className?: string;
  variant?: "select" | "inline";
  redirectTo?: string;
};

const UILanguagePicker = ({
  className,
  variant = "select",
  redirectTo = "/",
}: UILanguagePickerProps) => {
  const me = useMe();
  const router = useRouter();
  const [updateUser] = useUpdateUserMutation();
  if (!me?.user?.language) {
    return null;
  }

  const switchLanguage = (lang: string) => {
    if (lang === me.user!.language) return;
    updateUser({
      variables: { input: { language: lang as "en" | "fr" } },
    }).then(() => router.replace(redirectTo));
  };

  if (variant === "inline") {
    return (
      <div className={`flex gap-1 text-sm text-gray-400 ${className ?? ""}`}>
        {Object.entries(LANGUAGES).map(([code, label]) => (
          <button
            key={code}
            onClick={() => switchLanguage(code)}
            className={`px-1.5 py-0.5 rounded transition-colors ${
              me.user!.language === code
                ? "text-blue-600 font-semibold"
                : "hover:text-gray-600"
            }`}
          >
            {label}
          </button>
        ))}
      </div>
    );
  }

  return (
    <SimpleSelect
      className={className}
      value={me.user.language}
      required
      onChange={(e) => switchLanguage(e.target.value)}
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
