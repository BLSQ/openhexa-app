import { CodeBracketIcon } from "@heroicons/react/24/outline";
import Clipboard from "core/components/Clipboard";
import Popover from "core/components/Popover";
import Tabs from "core/components/Tabs";
import { useTranslation } from "next-i18next";

const CommandBox = ({ command }: { command: string }) => (
  <div className="flex items-center gap-2 rounded-md border border-gray-200 bg-gray-50 px-2.5 py-2">
    <code className="min-w-0 flex-1 select-all overflow-x-auto whitespace-nowrap font-mono text-xs text-gray-700">
      {command}
    </code>
    <Clipboard value={command} iconClassName="h-4 w-4 shrink-0 text-gray-400" />
  </div>
);

const SectionLabel = ({ children }: { children: React.ReactNode }) => (
  <div className="text-xs font-semibold uppercase tracking-wide text-gray-500">
    {children}
  </div>
);

type GitClonePopoverProps = {
  cloneUrl: string;
};

const GitClonePopover = ({ cloneUrl }: GitClonePopoverProps) => {
  const { t } = useTranslation();
  const cloneCommand = `git clone ${cloneUrl}`;

  return (
    <Popover
      placement="bottom-end"
      buttonClassName="inline-flex items-center gap-1.5 rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 transition-colors"
      trigger={
        <>
          <CodeBracketIcon className="h-4 w-4 text-gray-500" />
          {t("Clone")}
        </>
      }
      className="w-max max-w-[90vw]"
    >
      <div className="space-y-4">
        <div className="space-y-2">
          <SectionLabel>{t("Clone with HTTPS")}</SectionLabel>
          <CommandBox command={cloneCommand} />
        </div>

        <div className="space-y-2 border-t border-gray-100 pt-3">
          <div className="flex items-center justify-between gap-3">
            <SectionLabel>
              {t("Requires Git Credential Manager (one-time install)")}
            </SectionLabel>
            <a
              href="https://github.com/git-ecosystem/git-credential-manager/blob/main/docs/install.md"
              target="_blank"
              rel="noopener noreferrer"
              className="shrink-0 whitespace-nowrap text-xs text-blue-600 hover:underline"
            >
              {t("Other install options")}
            </a>
          </div>
          <Tabs>
            <Tabs.Tab label={t("macOS")}>
              <div className="pt-3">
                <CommandBox command="brew install --cask git-credential-manager" />
              </div>
            </Tabs.Tab>
            <Tabs.Tab label={t("Windows")}>
              <p className="pt-3 text-xs leading-relaxed text-gray-600">
                {t(
                  "Already included with Git for Windows — nothing to install.",
                )}
              </p>
            </Tabs.Tab>
            <Tabs.Tab label={t("Linux")}>
              <div className="space-y-2 pt-3">
                <p className="text-xs leading-relaxed text-gray-600">
                  {t("Debian/Ubuntu — download the latest .deb from the")}{" "}
                  <a
                    href="https://github.com/git-ecosystem/git-credential-manager/releases"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    {t("releases page")}
                  </a>
                  {t(", then run:")}
                </p>
                <CommandBox command="sudo dpkg -i gcm-linux_amd64.*.deb && git-credential-manager configure" />
              </div>
            </Tabs.Tab>
          </Tabs>
        </div>
      </div>
    </Popover>
  );
};

export default GitClonePopover;
