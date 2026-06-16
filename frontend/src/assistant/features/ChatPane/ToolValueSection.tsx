import { ArrowsPointingOutIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Clipboard from "core/components/Clipboard";
import Dialog from "core/components/Dialog";
import JsonView from "core/components/JsonView";
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "next-i18next";
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
  const semantic = resolveSemanticRenderer(value, ctx);
  const [mode, setMode] = useState<"pretty" | "raw">(semantic ? "pretty" : "raw");
  const [modalOpen, setModalOpen] = useState(false);
  const [overflowing, setOverflowing] = useState(false);
  const boxRef = useRef<HTMLDivElement>(null);

  const body = () =>
    mode === "pretty" && semantic ? (
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
    mode === "pretty" && isWideRenderer ? COLLAPSED_MAX_WIDE_PX : COLLAPSED_MAX_PX;
  const modalMaxWidth = isWideRenderer ? "max-w-6xl" : "max-w-3xl";

  const controls = (withExpand: boolean) => (
    <>
      {semantic && (
        <ViewToggle
          formattedLabel={t(semantic.label)}
          mode={mode}
          onChange={setMode}
        />
      )}
      {withExpand && canExpand && (
        <button
          type="button"
          onClick={() => setModalOpen(true)}
          title={t("Expand")}
          className="rounded-sm text-gray-400 transition-colors hover:text-gray-600"
        >
          <ArrowsPointingOutIcon className="h-3.5 w-3.5" />
        </button>
      )}
      <Clipboard value={rawText(value)} iconClassName="h-3.5 w-3.5 text-gray-400" />
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
        <div className="flex shrink-0 items-center gap-2">{controls(true)}</div>
      </div>

      <div
        ref={boxRef}
        className="relative w-full overflow-hidden"
        style={{ maxHeight: previewMaxPx }}
      >
        {body()}
        {overflowing && (
          <div className="absolute inset-x-0 bottom-0 flex justify-center bg-gradient-to-t from-white via-white/95 to-transparent pb-1 pt-8">
            <button
              type="button"
              onClick={() => setModalOpen(true)}
              className="rounded-md border border-gray-200 bg-white px-2.5 py-1 text-xs font-medium text-gray-600 shadow-sm hover:bg-gray-50"
            >
              {t("Show more")}
            </button>
          </div>
        )}
      </div>

      {modalOpen && (
        <Dialog open onClose={() => setModalOpen(false)} maxWidth={modalMaxWidth}>
          <Dialog.Title onClose={() => setModalOpen(false)}>
            <div className="flex items-center gap-3 text-base">
              <span>{label}</span>
              <div className="flex items-center gap-2">{controls(false)}</div>
            </div>
          </Dialog.Title>
          <Dialog.Content>{body()}</Dialog.Content>
        </Dialog>
      )}
    </div>
  );
}
