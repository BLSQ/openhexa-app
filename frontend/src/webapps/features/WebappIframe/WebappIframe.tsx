import clsx from "clsx";
import React, { useEffect, useMemo, useState } from "react";
import Spinner from "core/components/Spinner";

type WebappIframeProps = {
  url: string;
  className?: string;
  style?: React.CSSProperties;
};

const WebappIframe = ({ url, className, style }: WebappIframeProps) => {
  const [iframeLoading, setIframeLoading] = useState(true);

  useEffect(() => {
    setIframeLoading(true);
  }, [url]);

  const isSameOrigin = useMemo(() => {
    try {
      const { origin } = new URL(url);
      return origin === window.location.origin;
    } catch {
      return false;
    }
  }, [url]);

  const isSupersetDashboard = useMemo(() => {
    try {
      const { origin } = new URL(url);
      return (
        origin === window.location.origin &&
        url.includes("/superset/dashboard/")
      );
    } catch {
      return false;
    }
  }, [url]);

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
      className={clsx("flex justify-center items-center", className)}
      style={{ height: "90vh", ...style }}
    >
      {iframeLoading && <Spinner size="md" />}{" "}
      <iframe
        src={url}
        className={clsx("w-full h-full", iframeLoading && "hidden")}
        sandbox={sandboxPermissions}
        onLoad={() => setIframeLoading(false)}
        onError={() => setIframeLoading(false)}
        data-testid="webapp-iframe"
      />
    </div>
  );
};

export default WebappIframe;
