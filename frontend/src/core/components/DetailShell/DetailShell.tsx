import { createContext, ReactNode, RefObject, useContext, useRef } from "react";

type DetailShellContextValue = {
  containerRef: RefObject<HTMLDivElement>;
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
      <div className="flex h-full min-h-0 flex-col bg-white">{children}</div>
    </DetailShellContext.Provider>
  );
};

// Holds the side-by-side panes below the header; it is the reference the
// assistant dock resizes against.
const Body = ({ children }: { children: ReactNode }) => {
  const { containerRef } = useDetailShell();

  return (
    <div ref={containerRef} className="flex min-h-0 flex-1">
      {children}
    </div>
  );
};

const Main = ({ children }: { children: ReactNode }) => (
  <div className="flex min-w-0 flex-1 flex-col">{children}</div>
);

DetailShell.Body = Body;
DetailShell.Main = Main;

export default DetailShell;
