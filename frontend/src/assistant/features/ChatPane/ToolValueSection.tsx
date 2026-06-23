import { ArrowsPointingOutIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Clipboard from "core/components/Clipboard";
import Dialog from "core/components/Dialog";
import JsonView from "core/components/JsonView";
import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "next-i18next";
import { formatToolName, getToolLabels } from "assistant/helpers/toolNames";
import RendererBoundary from "./renderers/RendererBoundary";
import { resolveSemanticRenderer, RenderContext } from "./renderers";

const COLLAPSED_MAX_PX = 260;
const COLLAPSED_MAX_WIDE_PX = 380;

type Props = {
  label: string;
  value: unknown;
  ctx: RenderContext;
};

function rawText(value: unknown): string {
  if (typeof value === "string") return value;
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function ViewToggle({
  formattedLabel,
  mode,
  onChange,
}: {
  formattedLabel: string;
  mode: "pretty" | "raw";
  onChange: (mode: "pretty" | "raw") => void;
}) {
  const { t } = useTranslation();
  const options: { id: "pretty" | "raw"; label: string }[] = [
    { id: "pretty", label: formattedLabel },
    { id: "raw", label: t("Raw") },
  ];
  return (
    <div className="flex items-center rounded-md border border-gray-200 bg-white p-0.5">
      {options.map((opt) => (
        <button
          key={opt.id}
          type="button"
          onClick={() => onChange(opt.id)}
          className={clsx(
            "rounded px-1.5 py-0.5 text-[0.7rem] font-medium transition-colors",
            mode === opt.id
              ? "bg-gray-100 text-gray-700"
              : "text-gray-400 hover:text-gray-600",
          )}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

export default function ToolValueSection({ label, value, ctx }: Props) {
  const { t } = useTranslation();
  // ctx is rebuilt on every parent render, so depend on the stable fields the
  // resolver actually reads rather than the object identity.
  const semantic = useMemo(
    () => resolveSemanticRenderer(value, ctx),
    [value, ctx.toolName, ctx.kind, ctx.input],
  );
  const raw = useMemo(() => rawText(value), [value]);
  const defaultMode: "pretty" | "raw" = semantic ? "pretty" : "raw";
  const [mode, setMode] = useState<"pretty" | "raw">(defaultMode);
  const [modalMode, setModalMode] = useState<"pretty" | "raw">(defaultMode);
  const [modalOpen, setModalOpen] = useState(false);
  const [overflowing, setOverflowing] = useState(false);
  const boxRef = useRef<HTMLDivElement>(null);

  // The modal keeps its own view mode so toggling Raw/formatted there doesn't
  // also flip the inline conversation snippet. It opens showing whatever the
  // inline preview was last set to.
  const openModal = () => {
    setModalMode(mode);
    setModalOpen(true);
  };

  const body = (viewMode: "pretty" | "raw") =>
    viewMode === "pretty" && semantic ? (
      <RendererBoundary value={value}>
        {semantic.render(value, ctx)}
      </RendererBoundary>
    ) : (
      <JsonView value={value} maxHeight={null} hideCopy />
    );

  useEffect(() => {
    const el = boxRef.current;
    if (!el) return;
    const check = () => setOverflowing(el.scrollHeight > el.clientHeight + 2);
    check();
    if (typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(check);
    observer.observe(el);
    return () => observer.disconnect();
  }, [value, mode]);

  // A structured view always benefits from the roomy modal; raw/plain content
  // only needs it once it overflows the inline preview.
  const canExpand = !!semantic || overflowing;
  const isWideRenderer = !!semantic?.wide;
  // Taller inline preview only while the wide view is actually showing; modal
  // width stays stable so it doesn't jump when toggling to raw inside it.
  const previewMaxPx =
    mode === "pretty" && isWideRenderer
      ? COLLAPSED_MAX_WIDE_PX
      : COLLAPSED_MAX_PX;
  const toolLabel = formatToolName(ctx.toolName, getToolLabels(t));
  // Wide views (tables) commonly overflow horizontally without overflowing
  // vertically, so offer the modal even when the inline box isn't clipped.
  const showBottomCta = overflowing || (isWideRenderer && mode === "pretty");

  const controls = (
    withExpand: boolean,
    viewMode: "pretty" | "raw",
    onModeChange: (mode: "pretty" | "raw") => void,
  ) => (
    <>
      {semantic && (
        <ViewToggle
          formattedLabel={semantic.label(t)}
          mode={viewMode}
          onChange={onModeChange}
        />
      )}
      {withExpand && canExpand && (
        <button
          type="button"
          onClick={openModal}
          title={t("Expand")}
          className="rounded-sm text-gray-400 transition-colors hover:text-gray-600"
        >
          <ArrowsPointingOutIcon className="h-3.5 w-3.5" />
        </button>
      )}
      <Clipboard value={raw} iconClassName="h-3.5 w-3.5 text-gray-400" />
    </>
  );

  return (
    <div className="w-full space-y-1">
      {/* Header sits in its own row above the box; the box (not this row) owns
          the table's horizontal scroll, so the controls stay put on wide content. */}
      <div className="flex items-center justify-between gap-2">
        <span className="min-w-0 truncate text-[0.7rem] font-medium uppercase tracking-wide text-gray-400">
          {label}
        </span>
        <div className="flex shrink-0 items-center gap-2">
          {controls(true, mode, setMode)}
        </div>
      </div>

      <div
        ref={boxRef}
        className="relative w-full overflow-hidden"
        style={{ maxHeight: previewMaxPx }}
      >
        {body(mode)}
        {overflowing && (
          <div className="pointer-events-none absolute inset-x-0 bottom-0 h-10 bg-gradient-to-t from-white to-transparent" />
        )}
      </div>

      {showBottomCta && (
        <div className="flex justify-center pt-0.5">
          <button
            type="button"
            onClick={openModal}
            className="rounded-md border border-gray-200 bg-white px-2.5 py-1 text-xs font-medium text-gray-600 shadow-sm hover:bg-gray-50"
          >
            {overflowing ? t("Show more") : t("Expand")}
          </button>
        </div>
      )}

      {/* Always mounted with `open` toggled (not conditionally rendered) so
          headlessui can play the enter/leave transitions; conditional mounting
          would pop it in and out with no animation. */}
      <Dialog
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        maxWidth="max-w-[95vw]"
        // fitContent keeps the panel hugging the resizable box, so the backdrop
        // stays flush against it and clicking just outside closes the dialog.
        fitContent
        className={clsx(
          // Drag-resizable in both directions. It opens at a limited default
          // height (h-[75vh]) so there's space below the modal, but the user can
          // drag it taller — up to the panel cap from Dialog (calc(100vh-5rem)),
          // which keeps it inside the viewport.
          "resize overflow-auto h-[75vh] min-h-[300px] min-w-[400px] max-w-[90vw]",
          isWideRenderer ? "w-[1100px]" : "w-[760px]",
        )}
      >
        <Dialog.Title onClose={() => setModalOpen(false)}>
          <div className="flex items-center gap-3 text-base">
            <span className="font-medium text-gray-900">{toolLabel}</span>
            <span className="text-sm font-normal text-gray-400">{label}</span>
            <div className="flex items-center gap-2">
              {controls(false, modalMode, setModalMode)}
            </div>
          </div>
        </Dialog.Title>
        <Dialog.Content className="pb-4">{body(modalMode)}</Dialog.Content>
      </Dialog>
    </div>
  );
}
