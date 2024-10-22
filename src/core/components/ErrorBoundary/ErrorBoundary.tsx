import { ErrorBoundary as SentryErrorBoundary } from "@sentry/nextjs";
import clsx from "clsx";

export default function ErrorBoundary({
  children,
  fullScreen = true,
}: {
  children: React.ReactNode;
  fullScreen?: boolean;
}) {
  return (
    <SentryErrorBoundary
      fallback={
        <div
          className={clsx(
            "flex flex-col items-center justify-center p-6",
            fullScreen && " h-screen w-screen ",
          )}
        >
          <div className="space-y-2 text-center font-sans text-3xl font-normal text-gray-600">
            <p>Something went wrong.</p>
            <p className="text-2xl font-light text-gray-500">
              Try reloading the page and if the issue persists please contact
              your OpenHEXA administrators.
            </p>
          </div>
        </div>
      }
    >
      {children}
    </SentryErrorBoundary>
  );
}
