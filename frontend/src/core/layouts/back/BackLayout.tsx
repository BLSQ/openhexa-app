import clsx from "clsx";
import { useRouter } from "next/router";
import { ReactNode } from "react";
import BackLayoutHeader from "./BackLayoutHeader";

type BackLayoutProps = {
  title: string | ReactNode;
  children: ReactNode;
  onBack?: () => void;
  className?: string;
};

const BackLayout = ({
  children,
  title,
  onBack,
  className,
}: BackLayoutProps) => {
  const router = useRouter();
  const handleBack = () => {
    if (onBack) {
      return onBack();
    }
    if (window.history.length > 1) {
      return router.back();
    } else {
      return router.push("/workspaces");
    }
  };

  return (
    <div className="w-screen min-h-screen">
      <BackLayoutHeader onBack={handleBack} title={title} />
      <main
        className={clsx(
          "mt-8 w-full max-w-7xl mx-auto px-2 sm:px-6 lg:px-8",
          className,
        )}
      >
        {children}
      </main>
    </div>
  );
};

export default BackLayout;
