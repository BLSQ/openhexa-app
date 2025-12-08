import { MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import { useTranslation } from "next-i18next";
import { GetServerSidePropsContext } from "next";

export let isMac = false;

function getIsMac() {
  if (typeof window === "undefined") {
    return isMac;
  }
  const userAgent = window.navigator.userAgent;
  return userAgent.includes("Mac");
}

type InputSearchProps = {
  onClick: () => void;
};
const InputSearch = ({ onClick }: InputSearchProps) => {
  const { t } = useTranslation();
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-2 w-full px-3 py-2 text-sm bg-white hover:bg-gray-50 border border-gray-300 rounded-md transition-colors cursor-pointer"
    >
      <MagnifyingGlassIcon className="h-4 w-4 text-gray-500" />
      <span className="flex-1 text-left text-gray-500">{t("Search...")}</span>
      <kbd className="hidden sm:inline-flex items-center px-1.5 py-0.5 text-xs font-medium text-gray-500 bg-gray-100 border border-gray-300 rounded">
        {getIsMac() ? "⌘K" : "Ctrl+K"}
      </kbd>
    </button>
  );
};

InputSearch.prefetch = async (ctx: GetServerSidePropsContext) => {
  isMac = ctx.req.headers["user-agent"]?.includes("Mac") ?? false;
};

export default InputSearch;
