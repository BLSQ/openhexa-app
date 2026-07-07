import { useEffect, useState } from "react";

// Detect macOS on the client to show the right modifier symbol (⌘ vs Ctrl) in
// keyboard hints. Starts as `false` so the server render and first client
// render agree (no hydration mismatch), then resolves after mount.
const useIsMac = () => {
  const [isMac, setIsMac] = useState(false);

  useEffect(() => {
    setIsMac(window.navigator.userAgent.includes("Mac"));
  }, []);

  return isMac;
};

export default useIsMac;
