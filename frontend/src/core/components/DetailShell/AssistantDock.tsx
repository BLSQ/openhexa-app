import clsx from "clsx";
import useResizablePanel from "core/hooks/useResizablePanel";
import { ReactNode, useCallback, useEffect, useState } from "react";
import { useDetailShell } from "./DetailShell";

const hiddenKey = (storageKey: string) => `${storageKey}-hidden`;
const widthKey = (storageKey: string) => `${storageKey}-width`;

export const useAssistantDock = (storageKey: string) => {
  const [isOpen, setIsOpen] = useState(true);

  useEffect(() => {
    setIsOpen(window.localStorage.getItem(hiddenKey(storageKey)) !== "true");
  }, [storageKey]);

  const toggle = useCallback(() => {
    setIsOpen((wasOpen) => {
      window.localStorage.setItem(hiddenKey(storageKey), String(wasOpen));
      return !wasOpen;
    });
  }, [storageKey]);

  return { isOpen, toggle };
};

type AssistantDockProps = {
  storageKey: string;
  children: ReactNode;
};

const AssistantDock = ({ storageKey, children }: AssistantDockProps) => {
  const { containerRef } = useDetailShell();
  const { width, isDragging, startDragging, resetWidth } = useResizablePanel({
    storageKey: widthKey(storageKey),
    containerRef,
  });

  return (
    <>
      <div
        role="separator"
        aria-orientation="vertical"
        onMouseDown={(event) => {
          event.preventDefault();
          startDragging();
        }}
        onDoubleClick={resetWidth}
        className={clsx(
          "relative w-1 flex-none cursor-col-resize transition-colors",
          isDragging ? "bg-blue-500" : "bg-transparent hover:bg-blue-400",
        )}
      >
        <span className="absolute inset-y-0 -left-1 -right-1 block" />
      </div>
      <div className="flex flex-none flex-col" style={{ width }}>
        {children}
      </div>
    </>
  );
};

export default AssistantDock;
