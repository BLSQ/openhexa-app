import { CpuChipIcon } from "@heroicons/react/24/outline";
import Link from "core/components/Link";
import { useTranslation } from "next-i18next";

const McpHeaderLink = () => {
  const { t } = useTranslation();

  return (
    <Link
      href="/mcp"
      noStyle
      title={t("Tools exposed by the OpenHEXA MCP server")}
      className="flex shrink-0 cursor-pointer items-center gap-2 self-stretch rounded-md border border-gray-300 bg-white px-3 text-sm text-gray-500 transition-colors hover:bg-gray-50 hover:text-gray-700"
    >
      <CpuChipIcon className="h-4 w-4 shrink-0" />
      MCP
    </Link>
  );
};

export default McpHeaderLink;
