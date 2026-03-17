import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import CenteredLayout from "core/layouts/centered";
import Page from "core/components/Page";
import UILanguagePicker from "identity/features/UILanguagePicker";
import Image from "next/legacy/image";
import Link from "next/link";
import logo from "public/images/logo.svg";
import { ReactElement } from "react";
import { useTranslation } from "next-i18next";
import { GetServerSidePropsContext } from "next";

type Tool = {
  name: string;
  description: string;
  inputSchema: {
    type: string;
    properties: Record<string, { type: string }>;
    required: string[];
  };
};

type McpPageProps = {
  serverName: string;
  serverVersion: string;
  protocolVersion: string;
  tools: Tool[];
};

const McpToolsPage: NextPageWithLayout<McpPageProps> = ({
  serverName,
  serverVersion,
  protocolVersion,
  tools,
}) => {
  const { t } = useTranslation();

  return (
    <Page title={t("MCP Tools")}>
      <div className="w-full max-w-3xl">
        <div className="mb-2 flex justify-end">
          <UILanguagePicker variant="inline" redirectTo="/mcp" />
        </div>
        <div className="mb-6 flex items-center gap-4">
          <div className="relative h-12 w-32">
            <Image src={logo} layout="fill" alt="OpenHEXA" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {t("MCP Tools")}
            </h1>
            <p className="text-sm text-gray-500">
              {t("Tools exposed by the OpenHEXA MCP server")}
            </p>
          </div>
        </div>

        <div className="mb-6 flex items-center justify-between">
          <p className="text-xs text-gray-400">
            {serverName} v{serverVersion} &middot; Protocol {protocolVersion}{" "}
            &middot; {t("{{count}} tool", { count: tools.length })}
          </p>
          <Link
            href="/mcp/wiki"
            className="inline-flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-700"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M8 2v8M4 6l4 4 4-4M2 14h12" />
            </svg>
            {t("Install")}
          </Link>
        </div>

        {tools.length > 0 ? (
          <div className="space-y-3">
            {tools.map((tool) => {
              const properties = tool.inputSchema?.properties ?? {};
              const required = new Set(tool.inputSchema?.required ?? []);
              const params = Object.entries(properties);

              return (
                <div
                  key={tool.name}
                  className="rounded-lg border border-gray-200 p-5 transition-colors hover:border-blue-500"
                >
                  <div className="flex items-center gap-2">
                    <span className="font-semibold font-mono text-blue-600">
                      {tool.name}
                    </span>
                    <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">
                      {t("{{count}} param", { count: params.length })}
                    </span>
                  </div>
                  {tool.description && (
                    <p className="mt-2 text-sm leading-relaxed text-gray-700">
                      {tool.description}
                    </p>
                  )}
                  {params.length > 0 && (
                    <div className="mt-3">
                      <div className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-gray-500">
                        {t("Parameters")}
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {params.map(([name, prop]) => (
                          <span
                            key={name}
                            className="inline-flex items-center gap-1 rounded bg-gray-100 px-2 py-1 font-mono text-xs"
                          >
                            <span className="text-gray-900">{name}</span>
                            <span className="text-gray-500">{prop.type}</span>
                            {required.has(name) ? (
                              <span className="text-xs font-semibold text-red-600">
                                {t("required")}
                              </span>
                            ) : (
                              <span className="text-xs text-gray-400">
                                {t("optional")}
                              </span>
                            )}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="py-12 text-center text-gray-400">
            {t("No tools registered.")}
          </div>
        )}
      </div>
    </Page>
  );
};

McpToolsPage.getLayout = (page: ReactElement) => (
  <CenteredLayout>{page}</CenteredLayout>
);

export const getServerSideProps = createGetServerSideProps({
  requireAuth: false,
  getServerSideProps: async (ctx: GetServerSidePropsContext) => {
    const backendUrl =
      process.env.OPENHEXA_BACKEND_URL ?? "http://localhost:8000";
    try {
      const res = await fetch(`${backendUrl}/mcp/tools.json`);
      const data = await res.json();
      return {
        props: {
          serverName: data.server_name,
          serverVersion: data.server_version,
          protocolVersion: data.protocol_version,
          tools: data.tools,
        },
      };
    } catch {
      return {
        props: {
          serverName: "OpenHEXA",
          serverVersion: "0.0.1",
          protocolVersion: "",
          tools: [],
        },
      };
    }
  },
});

export default McpToolsPage;
