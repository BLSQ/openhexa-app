import { KeyboardEvent, useCallback } from "react";

interface UseInputKeyDownProps {
  onEscape: () => void;
  onCommandShiftEnter: () => void;
}

export default function useInputKeyDown({
  onEscape,
  onCommandShiftEnter,
}: UseInputKeyDownProps) {
  return useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onEscape();
      } else if (e.key === "Enter" && (e.shiftKey || e.metaKey)) {
        e.preventDefault();
        onCommandShiftEnter();
      }
    },
    [onEscape, onCommandShiftEnter],
  );
}
