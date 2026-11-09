import {
  Decoration,
  EditorView,
  GutterMarker,
  RangeSetBuilder,
  ViewPlugin,
  gutter,
} from "@uiw/react-codemirror";
import { ChevronDownIcon, ChevronRightIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import { useTranslation } from "next-i18next";
import { useCallback, useMemo, useRef, useState } from "react";
import FilesEditor from "workspaces/features/FilesEditor";
import { FilesEditor_FileFragment } from "workspaces/features/FilesEditor/FilesEditor.generated";
import { FileNode } from "workspaces/features/FilesEditor/types";
import { formatSeconds, getSlowestLines, LineTime, Profile } from "./profile";

class TimeMarker extends GutterMarker {
  constructor(
    private text: string,
    private share: number,
  ) {
    super();
  }

  eq(other: TimeMarker) {
    return other.text === this.text && other.share === this.share;
  }

  toDOM() {
    const element = document.createElement("span");
    element.textContent = this.text;
    // Lines that take a tenth of the slowest line's time or more stand out.
    element.style.color = this.share >= 0.1 ? "#c2410c" : "#9ca3af";
    return element;
  }
}

/**
 * Show the time spent on each line in the margin and highlight lines by their share of the
 * slowest line's time, as line profilers do.
 */
function lineTimes(times: [number, number][]) {
  const byLine = new Map(times);
  const slowest = Math.max(...times.map(([, milliseconds]) => milliseconds));
  const share = (line: number) => (byLine.get(line) ?? 0) / slowest;
  return [
    gutter({
      class: "cm-lineTimes",
      lineMarker(view, block) {
        const line = view.state.doc.lineAt(block.from).number;
        const milliseconds = byLine.get(line);
        return milliseconds
          ? new TimeMarker(formatSeconds(milliseconds / 1000), share(line))
          : null;
      },
      initialSpacer: () => new TimeMarker("00.0ms", 0),
    }),
    EditorView.decorations.of((view) => {
      const builder = new RangeSetBuilder<Decoration>();
      for (let line = 1; line <= view.state.doc.lines; line++) {
        const value = share(line);
        if (value > 0.005) {
          builder.add(
            view.state.doc.line(line).from,
            view.state.doc.line(line).from,
            Decoration.line({
              attributes: {
                style: `background-color: rgba(251, 146, 60, ${(0.08 + value * 0.42).toFixed(2)})`,
              },
            }),
          );
        }
      }
      return builder.finish();
    }),
    EditorView.theme({
      ".cm-lineTimes .cm-gutterElement": {
        padding: "0 0.75rem",
        textAlign: "right",
        fontVariantNumeric: "tabular-nums",
      },
    }),
  ];
}

function scrollToLine(line: number) {
  return ViewPlugin.define((view) => {
    // The editor cannot be scrolled while it is being created.
    requestAnimationFrame(() => {
      if (line <= view.state.doc.lines) {
        view.dispatch({
          effects: EditorView.scrollIntoView(view.state.doc.line(line).from, {
            y: "center",
          }),
        });
      }
    });
    return {};
  });
}

const SLOWEST_LINES = 5;

type CodeProfileProps = {
  profile: Profile;
  name: string;
  files: FilesEditor_FileFragment[];
};

const CodeProfile = ({ profile, name, files }: CodeProfileProps) => {
  const { t } = useTranslation();
  const editorRef = useRef<HTMLDivElement>(null);
  const slowestLines = useMemo(
    () =>
      getSlowestLines(profile, SLOWEST_LINES).filter(({ path }) =>
        files.some((file) => file.path === path),
      ),
    [profile, files],
  );
  const [isListOpen, setIsListOpen] = useState(false);
  const [target, setTarget] = useState<LineTime | undefined>(slowestLines[0]);
  const openFiles = useMemo(
    () =>
      files.map((file) => ({
        ...file,
        autoSelect: target ? file.path === target.path : file.autoSelect,
      })),
    [files, target],
  );
  // A new target, even on the same line, recreates the extensions, which scrolls the editor.
  const fileExtensions = useCallback(
    (file: FileNode) => {
      const times = profile.files[file.path];
      return [
        ...(times?.length ? [lineTimes(times)] : []),
        ...(target?.path === file.path ? [scrollToLine(target.line)] : []),
      ];
    },
    [profile, target],
  );
  const getCode = (path: string, line: number) =>
    files
      .find((file) => file.path === path)
      ?.content?.split("\n")
      [line - 1]?.trim();

  return (
    <div className="space-y-4">
      {slowestLines.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-gray-200">
          <button
            type="button"
            aria-expanded={isListOpen}
            className={clsx(
              "flex w-full items-center gap-1 bg-gray-50 px-3 py-2 text-xs font-medium tracking-wide text-gray-500 uppercase hover:text-gray-700",
              isListOpen && "border-b border-gray-200",
            )}
            onClick={() => setIsListOpen(!isListOpen)}
          >
            {isListOpen ? (
              <ChevronDownIcon className="h-4 w-4" />
            ) : (
              <ChevronRightIcon className="h-4 w-4" />
            )}
            {t("Slowest lines")}
          </button>
          {isListOpen && (
            <ul className="divide-y divide-gray-100">
              {slowestLines.map((lineTime) => {
                const isTarget =
                  target?.path === lineTime.path &&
                  target.line === lineTime.line;
                const share =
                  lineTime.milliseconds / slowestLines[0].milliseconds;
                return (
                  <li key={`${lineTime.path}:${lineTime.line}`}>
                    <button
                      type="button"
                      className={clsx(
                        "flex w-full items-center gap-3 border-l-2 px-3 py-2 text-left hover:bg-gray-50",
                        isTarget
                          ? "border-orange-400 bg-orange-50/40"
                          : "border-transparent",
                      )}
                      onClick={() => {
                        setTarget({ ...lineTime });
                        editorRef.current?.scrollIntoView({
                          behavior: "smooth",
                          block: "nearest",
                        });
                      }}
                    >
                      <span
                        className="w-16 shrink-0 rounded-sm px-2 py-0.5 text-right text-xs font-medium text-orange-900 tabular-nums"
                        // The same heat as the line in the editor.
                        style={{
                          backgroundColor: `rgba(251, 146, 60, ${(0.08 + share * 0.42).toFixed(2)})`,
                        }}
                      >
                        {formatSeconds(lineTime.milliseconds / 1000)}
                      </span>
                      <code className="min-w-0 flex-1 truncate text-xs text-gray-800">
                        {getCode(lineTime.path, lineTime.line)}
                      </code>
                      <span className="shrink-0 font-mono text-xs text-gray-400">
                        {lineTime.path}:{lineTime.line}
                      </span>
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      )}
      <div ref={editorRef}>
        <FilesEditor
          key={target?.path}
          name={name}
          files={openFiles}
          fileExtensions={fileExtensions}
          defaultSidebarCollapsed
        />
      </div>
      <p className="text-xs text-gray-500">
        {t(
          "Times are sampled every 10 ms: lines without a time took less than that in total.",
        )}
      </p>
    </div>
  );
};

export default CodeProfile;
