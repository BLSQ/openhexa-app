import { MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import Badge from "core/components/Badge";
import React from "react";
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
  isSidebarOpen: boolean;
  onClick: () => void;
};
const InputSearch = ({ isSidebarOpen, onClick }: InputSearchProps) => {
  const { t } = useTranslation();

  return isSidebarOpen ? (
    <div className="flex flex-col border-gray-200 bg-gray-800 p-2">
      <button
        onClick={onClick}
        className="text-gray-400 bg-gray-700 hover:bg-gray-600 flex gap-4 p-2 rounded items-center"
      >
        <MagnifyingGlassIcon className="h-4 text-gray-400 ml-2" />
        <span className="whitespace-nowrap overflow-hidden transition-opacity duration-200">
          {t("Search")} {getIsMac() ? "(⌘K)" : "(Ctrl+K)"}
        </span>
      </button>
    </div>
  ) : (
    <button
      onClick={onClick}
      className="relative flex justify-center px-2 py-2 text-gray-400 hover:bg-gray-700 hover:text-white group text-md font-medium"
    >
      <MagnifyingGlassIcon className="text-gray-400 h-7 w-7 m-2" />
      <div className="absolute inset-y-0 left-full ml-1.5 hidden h-full items-center text-xs opacity-0 transition-opacity group-hover:flex group-hover:opacity-100">
        <Badge className="text-white bg-gray-800 ring-gray-500/20">
          {t("Search")} {getIsMac() ? "(⌘K)" : "(Ctrl+K)"}
        </Badge>
      </div>
    </button>
  );
};

InputSearch.prefetch = async (ctx: GetServerSidePropsContext) => {
  isMac = ctx.req.headers["user-agent"]?.includes("Mac") ?? false;
};

export default InputSearch;
