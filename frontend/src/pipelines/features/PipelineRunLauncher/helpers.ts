import { DateTime } from "luxon";

export function formatElapsed(seconds: number) {
  const total = Math.max(0, Math.floor(seconds));
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const secs = String(total % 60).padStart(2, "0");
  return hours > 0
    ? `${hours}:${String(minutes).padStart(2, "0")}:${secs}`
    : `${minutes}:${secs}`;
}

export function formatStartedAt(executionDate?: string | null) {
  return executionDate
    ? DateTime.fromISO(executionDate).toLocaleString(DateTime.TIME_WITH_SECONDS)
    : "-";
}

// Finished runs report their own duration; active runs are measured against
// the wall clock so the timer keeps ticking between polls.
export function getRunElapsedSeconds(
  run: { executionDate?: string | null; duration?: number | null },
  isFinished: boolean,
  now: number,
) {
  if (isFinished && run.duration != null) {
    return run.duration;
  }
  if (!run.executionDate) {
    return 0;
  }
  return (now - DateTime.fromISO(run.executionDate).toMillis()) / 1000;
}
