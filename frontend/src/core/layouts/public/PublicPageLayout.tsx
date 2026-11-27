import Button from "core/components/Button";
import Page from "core/components/Page";
import PoweredByOpenHexa from "core/components/PoweredByOpenHexa";
import { OPENHEXA_WEBSITE_URL } from "core/hooks/useOpenhexaWebsiteUrl";
import useMe from "identity/hooks/useMe";
import { useTranslation } from "next-i18next";
import Head from "next/head";
import Image from "next/legacy/image";
import Link from "next/link";
import { useRouter } from "next/router";
import logoWithTextBlack from "public/images/logo_with_text_black.svg";
import { ReactNode } from "react";

type PublicPageLayoutProps = {
  title: string;
  children: ReactNode;
};

// Frame of the pages a permalink opens. They work without an account, so they
// stand on their own instead of using the workspace layout, which needs a
// workspace the visitor can open.
const PublicPageLayout = ({ title, children }: PublicPageLayoutProps) => {
  const { t } = useTranslation();
  const router = useRouter();
  const me = useMe();

  return (
    <Page title={title}>
      {/* A permalink is shared on purpose, not published: keep it out of
          search engines and do not lend it to the pages it links to. */}
      <Head>
        <meta name="robots" content="noindex, nofollow" />
      </Head>
      <div className="flex min-h-screen flex-col bg-gray-50">
        <header className="border-b border-gray-200 bg-white">
          <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
            <a
              href={OPENHEXA_WEBSITE_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="relative block h-8 w-28"
            >
              <Image
                src={logoWithTextBlack}
                layout="fill"
                objectFit="contain"
                objectPosition="left"
                alt="OpenHEXA"
              />
            </a>
            {me?.user ? (
              <Link
                href="/workspaces"
                className="text-sm text-blue-600 hover:underline"
              >
                {t("Go to my workspaces")}
              </Link>
            ) : (
              <div className="flex items-center gap-4">
                <a
                  href={OPENHEXA_WEBSITE_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Button size="sm">{t("Start a free trial")}</Button>
                </a>
                <Link
                  href={`/login?next=${encodeURIComponent(router.asPath)}`}
                  className="text-sm text-blue-600 hover:underline"
                >
                  {t("Log in")}
                </Link>
              </div>
            )}
          </div>
        </header>

        <main className="mx-auto w-full max-w-7xl flex-1 space-y-6 px-4 py-8 sm:px-6">
          {children}
        </main>

        <PoweredByOpenHexa />
      </div>
    </Page>
  );
};

export default PublicPageLayout;
