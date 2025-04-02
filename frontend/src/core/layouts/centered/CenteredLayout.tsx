import { ReactNode } from "react";

type CenteredLayoutProps = {
  children: ReactNode;
};

const CenteredLayout = ({ children }: CenteredLayoutProps) => {
  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      {children}
    </div>
  );
};

export default CenteredLayout;
