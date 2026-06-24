import { ErrorBoundary } from "@sentry/nextjs";
import { ReactNode } from "react";
import JsonView from "core/components/JsonView";

// Guards a semantic renderer against tool input/output shapes that drift from
// what it expects: if rendering throws, we fall back to the raw JSON view
// (and Sentry records the failure so we notice the structure change).
export default function RendererBoundary({
  value,
  children,
}: {
  value: unknown;
  children: ReactNode;
}) {
  return (
    <ErrorBoundary fallback={<JsonView value={value} maxHeight={null} />}>
      {children}
    </ErrorBoundary>
  );
}
