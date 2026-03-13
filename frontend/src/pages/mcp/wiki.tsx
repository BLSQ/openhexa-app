import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import Page from "core/components/Page";
import UILanguagePicker from "identity/features/UILanguagePicker";
import Image from "next/legacy/image";
import Link from "next/link";
import logo from "public/images/logo.svg";
import { ReactElement, useState } from "react";
import { useTranslation } from "next-i18next";

const TABS = [
  "gemini",
  "claude",
  "claude-code",
  "claude-desktop",
  "chatgpt",
] as const;
type Tab = (typeof TABS)[number];

const TAB_LABELS: Record<Tab, string> = {
  claude: "Claude",
  "claude-code": "Claude Code",
  "claude-desktop": "Claude Desktop",
  gemini: "Gemini CLI",
  chatgpt: "ChatGPT",
};

function CodeBlock({ text }: { text: string }) {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="relative mb-4 overflow-x-auto rounded-lg bg-slate-800 p-5 font-mono text-sm leading-relaxed text-slate-200">
      <button
        onClick={handleCopy}
        className="absolute right-2 top-2 rounded px-2.5 py-1.5 text-xs text-slate-400 transition-colors hover:bg-white/20 hover:text-white"
      >
        {copied ? (
          <span className="text-green-400">{t("Copied!")}</span>
        ) : (
          t("Copy")
        )}
      </button>
      <pre className="whitespace-pre-wrap">{text}</pre>
    </div>
  );
}

function VerifySection() {
  const { t } = useTranslation();
  return (
    <>
      <h2 className="mb-3 mt-6 text-lg font-semibold">{t("Verify")}</h2>
      <p className="mb-3 text-sm leading-relaxed text-gray-700">
        {t(
          "Try the following prompt to verify that the connection is working:",
        )}
      </p>
      <CodeBlock text={t("List my OpenHEXA workspaces")} />
    </>
  );
}

type McpWikiPageProps = {
  mcpUrl: string;
};

const McpWikiPage: NextPageWithLayout<McpWikiPageProps> = ({ mcpUrl }) => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<Tab>(TABS[0]);

  return (
    <Page title={t("MCP Setup Guide")}>
      <div className="w-full max-w-3xl">
        <div className="mb-4 flex items-center justify-between">
          <Link href="/mcp" className="text-sm text-blue-600 hover:underline">
            &larr; {t("Back to MCP Tools")}
          </Link>
          <UILanguagePicker variant="inline" redirectTo="/mcp/wiki" />
        </div>

        <div className="mb-6 flex items-center gap-4">
          <div className="relative h-12 w-32">
            <Image src={logo} layout="fill" alt="OpenHEXA" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {t("MCP Setup Guide")}
            </h1>
            <p className="text-sm text-gray-500">
              {t("Connect your AI assistant to OpenHEXA")}
            </p>
          </div>
        </div>

        <div className="-mb-0.5 flex border-b-2 border-gray-200">
          {TABS.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`border-b-2 px-5 py-3 text-sm font-medium transition-colors ${
                activeTab === tab
                  ? "border-blue-600 font-semibold text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-900"
              }`}
            >
              {TAB_LABELS[tab]}
            </button>
          ))}
        </div>

        <div className="pt-6">
          {activeTab === "claude" && (
            <div>
              <h2 className="mb-3 text-lg font-semibold">{t("Setup")}</h2>
              <p className="mb-3 text-sm leading-relaxed text-gray-700">
                {t(
                  "In Claude, open the Integrations menu, then click Add more integrations.",
                )}
              </p>
              <ol className="list-decimal space-y-2 pl-6 text-sm leading-relaxed text-gray-700">
                <li>
                  {t("Paste the following URL in the configuration field:")}
                </li>
              </ol>
              <div className="my-3">
                <CodeBlock text={mcpUrl} />
              </div>
              <ol
                start={2}
                className="list-decimal space-y-2 pl-6 text-sm leading-relaxed text-gray-700"
              >
                <li>{t("Click Connect.")}</li>
                <li>
                  {t(
                    "A browser window will open to authorize access to your OpenHEXA account.",
                  )}
                </li>
                <li>
                  {t(
                    "Once authorized, OpenHEXA tools will be available in your conversation.",
                  )}
                </li>
              </ol>

              <VerifySection />
            </div>
          )}

          {activeTab === "claude-code" && (
            <div>
              <h2 className="mb-3 text-lg font-semibold">{t("Setup")}</h2>
              <p className="mb-3 text-sm leading-relaxed text-gray-700">
                {t("Run the following command in your terminal:")}
              </p>
              <CodeBlock
                text={`claude mcp add openhexa --transport http ${mcpUrl}`}
              />

              <h2 className="mb-3 text-lg font-semibold">
                {t("Authenticate")}
              </h2>
              <p className="mb-3 text-sm leading-relaxed text-gray-700">
                {t("Start Claude Code:")}
              </p>
              <CodeBlock text="claude" />
              <p className="mb-3 text-sm leading-relaxed text-gray-700">
                {t("Then run the following command inside Claude Code:")}
              </p>
              <CodeBlock text="/mcp" />
              <p className="text-sm leading-relaxed text-gray-700">
                {t(
                  "Select openhexa and authenticate, a browser opens to complete the OAuth authorization. You should see openhexa listed with its tools.",
                )}
              </p>

              <VerifySection />
            </div>
          )}

          {activeTab === "claude-desktop" && (
            <div>
              <h2 className="mb-3 text-lg font-semibold">{t("Setup")}</h2>
              <p className="mb-3 text-sm leading-relaxed text-gray-700">
                {t(
                  "Open Claude Desktop settings and navigate to the MCP configuration file. Add the following to your claude_desktop_config.json:",
                )}
              </p>
              <CodeBlock
                text={JSON.stringify(
                  {
                    mcpServers: {
                      openhexa: {
                        url: mcpUrl,
                      },
                    },
                  },
                  null,
                  2,
                )}
              />

              <h2 className="mb-3 text-lg font-semibold">
                {t("Configuration file location")}
              </h2>
              <ul className="mb-4 list-disc space-y-1 pl-6 text-sm leading-relaxed text-gray-700">
                <li>
                  <strong>macOS:</strong>{" "}
                  <code className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs">
                    ~/Library/Application
                    Support/Claude/claude_desktop_config.json
                  </code>
                </li>
                <li>
                  <strong>Windows:</strong>{" "}
                  <code className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs">
                    %APPDATA%\Claude\claude_desktop_config.json
                  </code>
                </li>
              </ul>
              <p className="text-sm leading-relaxed text-gray-700">
                {t(
                  "Restart Claude Desktop. A browser window will open to authorize access when you first use an OpenHEXA tool.",
                )}
              </p>

              <VerifySection />
            </div>
          )}

          {activeTab === "gemini" && (
            <div>
              <h2 className="mb-3 text-lg font-semibold">{t("Setup")}</h2>
              <p className="mb-3 text-sm leading-relaxed text-gray-700">
                {t("Run the following command in your terminal:")}
              </p>
              <CodeBlock
                text={`gemini mcp add --transport http openhexa ${mcpUrl}`}
              />

              <h2 className="mb-3 text-lg font-semibold">
                {t("Authenticate")}
              </h2>
              <p className="mb-3 text-sm leading-relaxed text-gray-700">
                {t("Start Gemini CLI:")}
              </p>
              <CodeBlock text="gemini" />
              <p className="mb-3 text-sm leading-relaxed text-gray-700">
                {t("Then run the following command inside Gemini:")}
              </p>
              <CodeBlock text="/mcp auth openhexa" />
              <p className="text-sm leading-relaxed text-gray-700">
                {t(
                  "A browser window will open to complete the OAuth authorization.",
                )}
              </p>

              <VerifySection />
            </div>
          )}

          {activeTab === "chatgpt" && (
            <div>
              <h2 className="mb-3 text-lg font-semibold">{t("Setup")}</h2>
              <p className="mb-3 text-sm leading-relaxed text-gray-700">
                {t(
                  "In ChatGPT, click on the Tools menu, then select Add MCP tool.",
                )}
              </p>
              <ol className="list-decimal space-y-2 pl-6 text-sm leading-relaxed text-gray-700">
                <li>
                  {t("Paste the following URL in the configuration field:")}
                </li>
              </ol>
              <div className="my-3">
                <CodeBlock text={mcpUrl} />
              </div>
              <ol
                start={2}
                className="list-decimal space-y-2 pl-6 text-sm leading-relaxed text-gray-700"
              >
                <li>{t("Click Connect.")}</li>
                <li>
                  {t(
                    "A browser window will open to authorize access to your OpenHEXA account.",
                  )}
                </li>
                <li>
                  {t(
                    "Once authorized, OpenHEXA tools will be available in your conversation.",
                  )}
                </li>
              </ol>

              <VerifySection />
            </div>
          )}
        </div>
      </div>
    </Page>
  );
};

McpWikiPage.getLayout = (page: ReactElement) => (
  <div className="flex min-h-screen items-start justify-center px-4 py-12 sm:px-6 lg:px-8">
    {page}
  </div>
);

export const getServerSideProps = createGetServerSideProps({
  requireAuth: false,
  getServerSideProps: async (ctx) => {
    const proto =
      ctx.req.headers["x-forwarded-proto"] || (ctx.req.socket as any).encrypted
        ? "https"
        : "http";
    const host = ctx.req.headers["x-forwarded-host"] || ctx.req.headers.host;
    return {
      props: {
        mcpUrl: `${proto}://${host}/mcp/`,
      },
    };
  },
});

export default McpWikiPage;
