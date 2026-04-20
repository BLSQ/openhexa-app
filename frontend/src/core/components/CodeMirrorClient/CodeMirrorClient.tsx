// CodeMirror accesses browser-only globals at init/import time and cannot run on the
// server. This wrapper disables SSR so it is safe to use in server-rendered pages.
import dynamic from "next/dynamic";

const CodeMirrorClient = dynamic(() => import("@uiw/react-codemirror"), {
  ssr: false,
});

export default CodeMirrorClient;
