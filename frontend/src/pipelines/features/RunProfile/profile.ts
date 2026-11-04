import { formatDuration } from "core/helpers/time";
import { i18n } from "next-i18next";

export type ProfileSpan = [number, number, number, ProfileSpan[]];

export type Profile = {
  duration: number;
  frames: string[];
  lanes: { name: string; nodes: ProfileSpan[] }[];
  files: Record<string, [number, number][]>;
};

export type TimelineNode = {
  name: string;
  frame: string;
  start: number;
  duration: number;
  color: string;
  children: TimelineNode[];
};

export function buildTimeline(
  profile: Profile,
  spans: ProfileSpan[],
): TimelineNode[] {
  return spans.map(([index, start, end, children]) => {
    const frame = profile.frames[index];
    const duration = (end - start) / 1000;
    return {
      name: `${getFunctionName(frame)} · ${formatSeconds(duration)}`,
      frame,
      start: start / 1000,
      duration,
      color: getFrameColor(frame),
      children: buildTimeline(profile, children),
    };
  });
}

export function getLaneDuration(profile: Profile, spans: ProfileSpan[]) {
  return spans
    .filter(([frame]) => getFunctionName(profile.frames[frame]) !== "<module>")
    .reduce((total, [, start, end]) => total + (end - start) / 1000, 0);
}

export type LineTime = { path: string; line: number; milliseconds: number };

export function getSlowestLines(profile: Profile, limit: number): LineTime[] {
  return Object.entries(profile.files)
    .flatMap(([path, times]) =>
      times.map(([line, milliseconds]) => ({ path, line, milliseconds })),
    )
    .sort((a, b) => b.milliseconds - a.milliseconds)
    .slice(0, limit);
}

export function getFunctionName(frame: string) {
  const index = frame.lastIndexOf(" (");
  return index > 0 ? frame.slice(0, index) : frame;
}

export function getFrameColor(frame: string) {
  let hash = 0;
  for (const char of getFunctionName(frame)) {
    hash = (hash * 31 + char.charCodeAt(0)) | 0;
  }
  const hue = Math.abs(hash) % 50;
  return `hsl(${hue}, 80%, ${62 + (Math.abs(hash >> 8) % 12)}%)`;
}

export function formatSeconds(seconds: number) {
  if (seconds < 1) {
    return i18n!.t("{{value}}ms", { value: Math.round(seconds * 1000) });
  }
  if (seconds < 60) {
    return i18n!.t("{{value}}s", { value: seconds.toFixed(1) });
  }
  return formatDuration(Math.round(seconds));
}
