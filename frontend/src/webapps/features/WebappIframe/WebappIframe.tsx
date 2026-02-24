import clsx from "clsx";
import React, { useEffect, useMemo, useState } from "react";
import Spinner from "core/components/Spinner";
import { useTranslation } from "next-i18next";

type WebappIframeProps = {
  url: string;
  className?: string;
  style?: React.CSSProperties;
  showPoweredBy?: boolean;
};

const WebappIframe = ({
  url,
  className,
  style,
  showPoweredBy = false,
}: WebappIframeProps) => {
  const { t } = useTranslation();
  const [iframeLoading, setIframeLoading] = useState(true);
  const [safeUrl, setSafeUrl] = useState<string | null | undefined>(
    undefined,
  );

  useEffect(() => {
    if (!url) {
      setSafeUrl(null);
      return;
    }
    try {
      const resolvedUrl = new URL(url, window.location.origin);
      if (
        resolvedUrl.protocol === "http:" ||
        resolvedUrl.protocol === "https:"
      ) {
        setSafeUrl(resolvedUrl.toString());
      } else {
        setSafeUrl(null);
      }
    } catch {
      setSafeUrl(null);
    }
  }, [url]);

  useEffect(() => {
    setIframeLoading(true);
  }, [url]);

  const isSameOrigin = useMemo(() => {
    if (!safeUrl) {
      return false;
    }
    try {
      const { origin } = new URL(safeUrl);
      return origin === window.location.origin;
    } catch {
      return false;
    }
  }, [safeUrl]);

  const isSupersetDashboard = useMemo(() => {
    if (!safeUrl) {
      return false;
    }
    try {
      const { origin } = new URL(safeUrl);
      return (
        origin === window.location.origin &&
        safeUrl.includes("/superset/dashboard/")
      );
    } catch {
      return false;
    }
  }, [safeUrl]);
  if (safeUrl === undefined) {
    return (
      <div
        className={clsx("flex flex-col", className)}
        style={{ height: "90vh", ...style }}
      >
        <div className="flex flex-1 justify-center items-center">
          <Spinner size="md" />
        </div>
      </div>
    );
  }

  if (safeUrl === null) {
    return (
      <div
        className={clsx("flex flex-col", className)}
        style={{ height: "90vh", ...style }}
      >
        <div className="flex flex-1 items-center justify-center text-sm text-gray-500">
          {t("The provided URL is invalid or not allowed.")}
        </div>
      </div>
    );
  }


  const commonPermissions =
    "allow-forms allow-popups allow-downloads allow-presentation allow-modals allow-scripts";

  // Do not allow same origin requests if it's an OpenHexa URL.
  // Note: Exceptionally allow it for Superset dashboards since using "allow-same-origin"
  // without "allow-scripts" is a no-go for Superset. The embedding SDK adds both
  // to the sandbox param and they appear required for proper loading of the page:
  // https://github.com/apache/superset/blob/0aa48b656446764b2e71d9d65cc14365398faa8b/superset-embedded-sdk/src/index.ts#L170-L171
  const sandboxPermissions =
    isSameOrigin && !isSupersetDashboard
      ? commonPermissions
      : `${commonPermissions} allow-same-origin`;

  return (
    <div
      className={clsx("flex flex-col", className)}
      style={{ height: "90vh", ...style }}
    >
      <div className="flex flex-1 justify-center items-center">
        {iframeLoading && <Spinner size="md" />}{" "}
        <iframe
          src={safeUrl}
          className={clsx("w-full h-full", iframeLoading && "hidden")}
          sandbox={sandboxPermissions}
          onLoad={() => setIframeLoading(false)}
          onError={() => setIframeLoading(false)}
          data-testid="webapp-iframe"
        />
      </div>
      {showPoweredBy && (
        <div className="flex items-center justify-center border-t bg-gray-50 py-2 text-xs text-gray-500">
          {t("Powered by")}{" "}
          <a
            href="https://www.openhexa.com"
            target="_blank"
            rel="noopener noreferrer"
            className="ml-1 flex items-center gap-1 font-medium text-blue-600 hover:text-blue-500"
          >
            <img
              src="/images/logo.svg"
              alt="OpenHEXA"
              className="h-4 w-4"
            />
            OpenHEXA
          </a>
        </div>
      )}
    </div>
  );
};

export default WebappIframe;
