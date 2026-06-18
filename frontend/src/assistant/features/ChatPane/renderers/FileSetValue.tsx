import { ChevronRightIcon, DocumentIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import { useState } from "react";
import { useTranslation } from "next-i18next";
import CodeValue from "./CodeValue";

export type FileEntry = {
  name?: string;
  path?: string;
  content: string;
};

function fileName(file: FileEntry, index: number): string {
  return file.name ?? file.path ?? `file ${index + 1}`;
}

export default function FileSetValue({
  files,
  deleted = [],
}: {
  files: FileEntry[];
  deleted?: string[];
}) {
  const { t } = useTranslation();
  // A single proposed file is almost always the thing to read, so open it up
  // front — unless deletions share the view, where neither is the obvious focus.
  const [open, setOpen] = useState<Record<number, boolean>>(
    files.length === 1 && deleted.length === 0 ? { 0: true } : {},
  );

  return (
    <div className="space-y-2">
      {files.length > 0 && (
        <div className="divide-y divide-gray-100 rounded-md border border-gray-200 bg-white">
          {files.map((file, i) => {
            const name = fileName(file, i);
            const isOpen = !!open[i];
            const lines = file.content.split("\n").length;
            return (
              <div key={i}>
                <button
                  type="button"
                  onClick={() => setOpen((o) => ({ ...o, [i]: !o[i] }))}
                  aria-expanded={isOpen}
                  className="flex w-full items-center gap-1.5 px-2.5 py-1.5 text-left text-xs hover:bg-gray-50"
                >
                  <ChevronRightIcon
                    className={clsx(
                      "h-3.5 w-3.5 shrink-0 text-gray-400 transition-transform",
                      isOpen && "rotate-90",
                    )}
                  />
                  <DocumentIcon className="h-4 w-4 shrink-0 text-gray-400" />
                  <span className="truncate font-mono text-gray-700">
                    {name}
                  </span>
                  <span className="ml-auto shrink-0 tabular-nums text-gray-400">
                    {t("{{count}} lines", { count: lines })}
                  </span>
                </button>
                {isOpen && (
                  <div className="px-2.5 pb-2">
                    <CodeValue content={file.content} fileName={name} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {deleted.length > 0 && (
        <div className="space-y-1">
          <div className="text-[0.7rem] font-medium uppercase tracking-wide text-gray-400">
            {t("Deleted files")}
          </div>
          <div className="divide-y divide-gray-100 rounded-md border border-gray-200 bg-white">
            {deleted.map((name) => (
              <div
                key={name}
                className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs"
              >
                <DocumentIcon className="h-4 w-4 shrink-0 text-red-300" />
                <span className="truncate font-mono text-red-400 line-through">
                  {name}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
