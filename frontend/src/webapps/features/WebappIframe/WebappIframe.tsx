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

  const commonPermissions =
    "allow-forms allow-popups allow-downloads allow-presentation allow-modals allow-scripts";
  const sandboxPermissions = isSameOrigin
    ? commonPermissions // Do not allow same origin requests if it's an OpenHexa URL
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
