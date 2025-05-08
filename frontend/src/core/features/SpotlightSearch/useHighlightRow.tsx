import { useEffect, RefObject } from "react";

const useHighlightRow = (
  resultRefs: RefObject<(HTMLDivElement | null)[]>,
  highlightedIndex: number,
  dependencies: any[] = [],
) => {
  useEffect(() => {
    resultRefs.current?.forEach((ref, index) => {
      const row = ref?.parentElement?.parentElement;
      if (row) {
        if (index === highlightedIndex) {
          row.className = "bg-blue-100/50 outline-solid outline-blue-500/50"; // Highlight the current row
          ref?.focus();
        } else {
          row.className = ""; // Reset other rows
        }
      }
    });
  }, [highlightedIndex, resultRefs, ...dependencies]);
};

export default useHighlightRow;
