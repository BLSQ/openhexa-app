import { useEffect, useState } from "react";

import { useRouter } from "next/router";
import Spinner from "core/components/Spinner";
import { useTranslation } from "next-i18next";

const OverlayProgress = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [showDots, setShowDots] = useState(0);
  const router = useRouter();
  const { t } = useTranslation();

  useEffect(() => {
    const handleRouteChangeStart = (url: string) => {
      const { workspaceSlug } = router.query as {
        workspaceSlug: string | undefined;
      };

      if (!workspaceSlug || !url.includes(workspaceSlug)) {
        setIsVisible(true);
      }
    };

    const handleRouteChangeEnd = () => setIsVisible(false);

    router.events.on("routeChangeStart", handleRouteChangeStart);
    router.events.on("routeChangeComplete", handleRouteChangeEnd);
    router.events.on("routeChangeError", handleRouteChangeEnd);

    return () => {
      router.events.off("routeChangeStart", handleRouteChangeStart);
      router.events.off("routeChangeComplete", handleRouteChangeEnd);
      router.events.off("routeChangeError", handleRouteChangeEnd);
    };
  }, [router]);

  useEffect(() => {
    if (isVisible) {
      setShowDots(0);
      const interval = setInterval(() => {
        setShowDots((prev) => prev + 1);
      }, 250);
      return () => clearInterval(interval);
    }
  }, [isVisible]);

  if (!isVisible) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-800/50 backdrop-blur-sm">
      <div className="flex items-center space-x-2">
        <Spinner size="sm" className="text-white" />
        <p className="text-lg text-white">
          {t("Switching workspace")} {".".repeat(showDots)}
        </p>
      </div>
    </div>
  );
};

export default OverlayProgress;
