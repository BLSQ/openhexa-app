import { CodeBracketIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import { Classes as ButtonClasses } from "core/components/Button";
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

const getProviderCommand = (repositoryUrl: string): string | null => {
  try {
    const { origin } = new URL(repositoryUrl);
    return `git config --global credential.${origin}.provider generic`;
  } catch {
    return null;
  }
};

type GitClonePopoverProps = {
  repositoryUrl: string;
};

const GitClonePopover = ({ repositoryUrl }: GitClonePopoverProps) => {
  const { t } = useTranslation();
  const cloneCommand = `git clone ${repositoryUrl}`;
  const providerCommand = getProviderCommand(repositoryUrl);

  return (
    <Popover
      placement="bottom-end"
      buttonClassName={clsx(
        ButtonClasses.base,
        ButtonClasses.md,
        ButtonClasses.white,
        "rounded-sm focus:outline-hidden focus:ring-2 focus:ring-offset-2",
      )}
      trigger={
        <>
          <CodeBracketIcon className="-ml-1 mr-1.5 h-4 w-4" />
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
                <CommandBox command="sudo dpkg -i gcm-linux-*.deb && git-credential-manager configure" />
                <p className="text-xs leading-relaxed text-gray-600">
                  {t(
                    "Note: Linux has no default credential store, so pick one or GCM will fall back to a plain username/password prompt:",
                  )}
                </p>
                <CommandBox command="git config --global credential.credentialStore secretservice" />
              </div>
            </Tabs.Tab>
          </Tabs>
          {providerCommand && (
            <div className="space-y-2 pt-1">
              <p className="text-xs leading-relaxed text-gray-600">
                {t(
                  "Optional — run this to force Git Credential Manager to sign in through OpenHEXA:",
                )}
              </p>
              <CommandBox command={providerCommand} />
            </div>
          )}
        </div>
      </div>
    </Popover>
  );
};

export default GitClonePopover;
