import { ErrorBoundary as SentryErrorBoundary } from "@sentry/nextjs";
import Title from "../Title";

export default function ErrorBoundary({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <SentryErrorBoundary
      fallback={
        <div className="flex h-screen w-screen flex-col items-center justify-center">
          <div className="space-y-2 text-center font-sans text-3xl font-normal text-gray-600">
            <p>Something went wrong.</p>
            <p className="text-2xl font-light text-gray-500">
              Try reloading the page and if the issue persists please contact
              your OpenHexa administrators.
            </p>
          </div>
        </div>
      }
    >
      {children}
    </SentryErrorBoundary>
  );
}
