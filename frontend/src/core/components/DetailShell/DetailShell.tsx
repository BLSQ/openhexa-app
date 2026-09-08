import { createContext, ReactNode, RefObject, useContext, useRef } from "react";

type DetailShellContextValue = {
  containerRef: RefObject<HTMLDivElement | null>;
};

const DetailShellContext = createContext<DetailShellContextValue | null>(null);

export const useDetailShell = () => {
  const context = useContext(DetailShellContext);
  if (!context) {
    throw new Error("useDetailShell must be used within a <DetailShell>");
  }
  return context;
};

type DetailShellProps = {
  children: ReactNode;
};

const DetailShell = ({ children }: DetailShellProps) => {
  const containerRef = useRef<HTMLDivElement>(null);

  return (
    <DetailShellContext.Provider value={{ containerRef }}>
      <div ref={containerRef} className="flex h-full min-h-0 bg-white">
        {children}
      </div>
    </DetailShellContext.Provider>
  );
};

const Main = ({ children }: { children: ReactNode }) => (
  <div className="flex min-w-0 flex-1 flex-col">{children}</div>
);

DetailShell.Main = Main;

export default DetailShell;
