import useMe from "identity/hooks/useMe";
import { useTranslation } from "next-i18next";
import Image from "next/legacy/image";
import Link from "next/link";
import { useRouter } from "next/router";
import logo from "public/images/logo.svg";
import { ReactNode } from "react";

type PublicLayoutProps = {
  children: ReactNode;
};

// Chrome of the permalink pages (public datasets, saved queries, pipelines).
// They work without an account, so they stand on their own instead of using
// the workspace layout, which needs a workspace the visitor can open. The only
// navigation offered is a way in: a login link, or the workspaces for members.
const PublicLayout = ({ children }: PublicLayoutProps) => {
  const { t } = useTranslation();
  const router = useRouter();
  const me = useMe();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <Link href="/" className="relative block h-8 w-24">
            <Image src={logo} layout="fill" alt="OpenHEXA" />
          </Link>
          {me?.user ? (
            <Link
              href="/workspaces"
              className="text-sm text-blue-600 hover:underline"
            >
              {t("Go to my workspaces")}
            </Link>
          ) : (
            <Link
              href={`/login?next=${encodeURIComponent(router.asPath)}`}
              className="text-sm text-blue-600 hover:underline"
            >
              {t("Log in")}
            </Link>
          )}
        </div>
      </header>
      <main className="mx-auto max-w-7xl space-y-6 px-4 py-8 sm:px-6">
        {children}
      </main>
    </div>
  );
};

export default PublicLayout;
