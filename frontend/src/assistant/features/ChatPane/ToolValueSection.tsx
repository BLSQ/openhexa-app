import { ArrowsPointingOutIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Clipboard from "core/components/Clipboard";
import Dialog from "core/components/Dialog";
import JsonView from "core/components/JsonView";
import {
  PointerEvent as ReactPointerEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { useTranslation } from "next-i18next";
import { formatToolName, getToolLabels } from "assistant/helpers/toolNames";
import RendererBoundary from "./renderers/RendererBoundary";
import { resolveSemanticRenderer, RenderContext } from "./renderers";

const COLLAPSED_MAX_PX = 260;
const COLLAPSED_MAX_WIDE_PX = 380;

// Modal resize bounds. MIN_* match the dialog's floor; the max is derived from
// the viewport at drag time (95% wide, and the same `100vh - 5rem` cap the
// Dialog panel enforces) so the box always stays on-screen.
const MODAL_MIN_WIDTH = 400;
const MODAL_MIN_HEIGHT = 300;
const MODAL_VIEWPORT_MARGIN_PX = 80;
const MODAL_DEFAULT_WIDTH = 760;
const MODAL_DEFAULT_WIDE_WIDTH = 1100;
const MODAL_DEFAULT_HEIGHT_RATIO = 0.75;

type ModalSize = { width: number; height: number };

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
  // null until the modal is first opened, at which point it's seeded from the
  // viewport; drag handles then drive it. Persists across opens so the box
  // reopens at the size the user last left it.
  const [modalSize, setModalSize] = useState<ModalSize | null>(null);
  const boxRef = useRef<HTMLDivElement>(null);

  const isWideRenderer = !!semantic?.wide;

  // The modal keeps its own view mode so toggling Raw/formatted there doesn't
  // also flip the inline conversation snippet. It opens showing whatever the
  // inline preview was last set to.
  const openModal = () => {
    setModalMode(mode);
    setModalSize(
      (prev) =>
        prev ?? {
          width: Math.min(
            isWideRenderer ? MODAL_DEFAULT_WIDE_WIDTH : MODAL_DEFAULT_WIDTH,
            window.innerWidth * 0.95,
          ),
          height: Math.round(
            window.innerHeight * MODAL_DEFAULT_HEIGHT_RATIO,
          ),
        },
    );
    setModalOpen(true);
  };

  const startResize = (
    e: ReactPointerEvent,
    edges: { right?: boolean; bottom?: boolean },
  ) => {
    e.preventDefault();
    const startX = e.clientX;
    const startY = e.clientY;
    const start = modalSize ?? {
      width: isWideRenderer ? MODAL_DEFAULT_WIDE_WIDTH : MODAL_DEFAULT_WIDTH,
      height: Math.round(window.innerHeight * MODAL_DEFAULT_HEIGHT_RATIO),
    };
    const maxW = window.innerWidth * 0.95;
    const maxH = window.innerHeight - MODAL_VIEWPORT_MARGIN_PX;

    const onMove = (ev: PointerEvent) => {
      // The panel is horizontally centered, so the right edge moves at half the
      // width delta (both sides shift) — double the X delta so it tracks the
      // cursor. Vertically the panel is top-anchored, so the bottom edge already
      // moves 1:1 with the height delta; no doubling there.
      setModalSize({
        width: edges.right
          ? Math.max(
              MODAL_MIN_WIDTH,
              Math.min(start.width + (ev.clientX - startX) * 2, maxW),
            )
          : start.width,
        height: edges.bottom
          ? Math.max(
              MODAL_MIN_HEIGHT,
              Math.min(start.height + (ev.clientY - startY), maxH),
            )
          : start.height,
      });
    };
    const onUp = () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
      document.body.style.userSelect = "";
    };
    document.body.style.userSelect = "none";
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
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
        // Drag-resizable via the custom handles below. Until first opened the
        // box uses its default classes; once a size exists it's driven by state
        // and capped by the Dialog's own `100vh - 5rem` height limit.
        style={
          modalSize
            ? { width: modalSize.width, height: modalSize.height }
            : undefined
        }
        className={clsx(
          "relative overflow-hidden min-h-[300px] min-w-[400px] max-w-[95vw]",
          !modalSize && "h-[75vh]",
          !modalSize && (isWideRenderer ? "w-[1100px]" : "w-[760px]"),
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

        {/* Resize handles: thin hit-targets on the right and bottom edges, each
            showing a subtle gray highlight on hover. The corner is an invisible
            target rendered first so it acts as a `peer` for the two strips —
            hovering it lights up BOTH at once (an L at the corner) to signal a
            two-axis resize, instead of a button-like grip. */}
        <div
          onPointerDown={(e) => startResize(e, { right: true, bottom: true })}
          title={t("Drag to resize")}
          className="peer/corner absolute bottom-0 right-0 z-10 flex h-4 w-4 cursor-nwse-resize items-end justify-end p-0.5 text-gray-400 transition-colors hover:text-gray-600"
        >
          <svg
            viewBox="0 0 12 12"
            className="h-3 w-3"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.25"
            strokeLinecap="round"
            aria-hidden="true"
          >
            <path d="M11 4 4 11 M11 7 7 11 M11 10 10 11" />
          </svg>
        </div>
        <div
          onPointerDown={(e) => startResize(e, { right: true })}
          className="absolute inset-y-0 right-0 w-1.5 cursor-ew-resize transition-colors hover:bg-gray-200/70 peer-hover/corner:bg-gray-200/70"
        />
        <div
          onPointerDown={(e) => startResize(e, { bottom: true })}
          className="absolute inset-x-0 bottom-0 h-1.5 cursor-ns-resize transition-colors hover:bg-gray-200/70 peer-hover/corner:bg-gray-200/70"
        />
      </Dialog>
    </div>
  );
}
