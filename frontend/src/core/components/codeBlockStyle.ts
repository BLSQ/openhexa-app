import type { CSSProperties } from "react";

// Shared visual style for the inline code/JSON blocks rendered through
// react-syntax-highlighter (JsonView and the assistant CodeValue renderer), so
// the two stay pixel-identical and can't drift apart.
export const CODE_BLOCK_STYLE: CSSProperties = {
  margin: 0,
  borderRadius: "0.375rem",
  fontSize: "0.75rem",
  background: "#ffffff",
  border: "1px solid #e5e7eb",
  padding: "0.625rem 0.75rem",
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
};
