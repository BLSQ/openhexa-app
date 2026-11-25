import { ArrowUpIcon } from "@heroicons/react/24/outline";
import { useTranslation } from "next-i18next";

const GETTING_STARTED_VIDEO_IDS: Record<string, string> = {
  en: "xVP4HGJByIw",
  fr: "Lr_hRqaC-vw",
};

type GettingStartedPlaceholderProps = {
  canCreateWorkspace: boolean;
};

/**
 * Shown instead of the workspaces list when an organization has none yet, to
 * walk new users through creating their first workspace.
 */
const GettingStartedPlaceholder = ({
  canCreateWorkspace,
}: GettingStartedPlaceholderProps) => {
  const { t, i18n } = useTranslation();
  const language = i18n?.language?.split("-")[0] ?? "en";
  const videoId =
    GETTING_STARTED_VIDEO_IDS[language] ?? GETTING_STARTED_VIDEO_IDS.en;

  return (
    <div className="flex flex-col gap-4 pb-8">
      {/* Points at the "Create Workspace" button in the page header so the page keeps a single CTA. */}
      {canCreateWorkspace && (
        <div className="flex items-center justify-end gap-2 pr-8 text-sm font-medium text-blue-600">
          {t("Create your first workspace")}
          <ArrowUpIcon className="h-5 w-5 animate-bounce" />
        </div>
      )}
      {/* The @tailwindcss/aspect-ratio plugin disables Tailwind's `aspect-video` utility. */}
      <div className="mx-auto [aspect-ratio:16/9] w-full max-w-6xl overflow-hidden rounded-lg bg-gray-900 shadow-lg ring-1 ring-gray-900/10">
        {/* youtube-nocookie avoids setting tracking cookies until the user plays the video. */}
        <iframe
          className="h-full w-full"
          src={`https://www.youtube-nocookie.com/embed/${videoId}?rel=0&hl=${language}`}
          title={t("Getting started with OpenHEXA")}
          loading="lazy"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          referrerPolicy="strict-origin-when-cross-origin"
          allowFullScreen
        />
      </div>
    </div>
  );
};

export default GettingStartedPlaceholder;
