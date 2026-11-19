import { ReactNode } from "react";
import { useTranslation } from "next-i18next";

// TODO(HEXA-1890): temporary test video for both languages; replace with the
// EN/FR "Getting started" videos once they are uploaded to YouTube.
const GETTING_STARTED_VIDEO_IDS: Record<string, string> = {
  en: "MKY2M78uNNE",
  fr: "MKY2M78uNNE",
};

type GettingStartedPlaceholderProps = {
  action: ReactNode;
};

/**
 * Shown instead of the workspaces list when an organization has none yet, to
 * walk new users through creating their first workspace.
 */
const GettingStartedPlaceholder = ({
  action,
}: GettingStartedPlaceholderProps) => {
  const { t, i18n } = useTranslation();
  const language = i18n?.language?.split("-")[0] ?? "en";
  const videoId =
    GETTING_STARTED_VIDEO_IDS[language] ?? GETTING_STARTED_VIDEO_IDS.en;

  return (
    <div className="mx-auto flex max-w-3xl flex-col items-center gap-6 py-8 text-center">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">
          {t("Get started with OpenHEXA")}
        </h2>
        <p className="mt-2 text-sm text-gray-500">
          {t(
            "Workspaces are where your team collaborates on data, pipelines and notebooks. Watch this short video, then create your first workspace.",
          )}
        </p>
      </div>
      {/* The @tailwindcss/aspect-ratio plugin disables Tailwind's `aspect-video` utility. */}
      <div className="[aspect-ratio:16/9] w-full overflow-hidden rounded-lg bg-gray-900 shadow-lg ring-1 ring-gray-900/10">
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
      {action}
    </div>
  );
};

export default GettingStartedPlaceholder;
