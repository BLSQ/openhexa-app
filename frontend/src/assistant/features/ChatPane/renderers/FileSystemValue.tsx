import { FolderIcon } from "@heroicons/react/24/solid";
import { DocumentIcon } from "@heroicons/react/24/outline";
import { DateTime } from "luxon";
import { Row } from "./tabular";

function isDirectory(file: Row): boolean {
  const type = typeof file.type === "string" ? file.type.toLowerCase() : "";
  if (type.includes("dir") || type.includes("folder")) return true;
  const name = (file.name ?? file.path ?? file.key) as string | undefined;
  return typeof name === "string" && name.endsWith("/");
}

function displayName(file: Row): string {
  const raw = (file.name ?? file.path ?? file.key ?? "") as string;
  const trimmed = raw.replace(/\/$/, "");
  const segments = trimmed.split("/");
  return segments[segments.length - 1] || trimmed || "—";
}

function humanSize(bytes: unknown): string {
  if (typeof bytes !== "number" || !Number.isFinite(bytes) || bytes <= 0) return "";
  const units = ["B", "KB", "MB", "GB", "TB"];
  let size = bytes;
  let unit = 0;
  while (size >= 1024 && unit < units.length - 1) {
    size /= 1024;
    unit += 1;
  }
  return `${unit === 0 ? size : size.toFixed(1)} ${units[unit]}`;
}

function formatDate(value: unknown): string {
  if (typeof value !== "string") return "";
  const dt = DateTime.fromISO(value);
  return dt.isValid ? dt.toLocaleString(DateTime.DATE_MED) : "";
}

export default function FileSystemValue({ files }: { files: Row[] }) {
  return (
    <ul className="divide-y divide-gray-100 rounded-md border border-gray-200 bg-white">
      {files.map((file, i) => {
        const dir = isDirectory(file);
        const size = dir ? "" : humanSize(file.size);
        const date = formatDate(file.updatedAt ?? file.updated_at);
        return (
          <li
            key={i}
            className="flex items-center gap-2 px-2.5 py-1.5 text-xs text-gray-700"
          >
            {dir ? (
              <FolderIcon className="h-4 w-4 shrink-0 text-blue-400" />
            ) : (
              <DocumentIcon className="h-4 w-4 shrink-0 text-gray-400" />
            )}
            <span className="truncate font-medium text-gray-800">
              {displayName(file)}
            </span>
            <span className="ml-auto shrink-0 tabular-nums text-gray-400">
              {size}
            </span>
            {date && (
              <span className="hidden w-24 shrink-0 text-right text-gray-400 sm:inline">
                {date}
              </span>
            )}
          </li>
        );
      })}
    </ul>
  );
}
