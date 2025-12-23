import { ApolloProvider } from "@apollo/client";
import { setUser } from "@sentry/nextjs";
import ErrorBoundary from "core/components/ErrorBoundary/ErrorBoundary";
import { useApollo } from "core/helpers/apollo";
import { AppPropsWithLayout } from "core/helpers/types";
import DefaultLayout from "core/layouts/default";
import { MeProvider } from "identity/hooks/useMe";
import { Settings } from "luxon";
import { appWithTranslation } from "next-i18next";
import Head from "next/head";
import NavigationProgress from "nextjs-progressbar";
import { useMemo, useEffect } from "react";
import { CookiesProvider } from "react-cookie";
import { Cookies } from "react-cookie";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "../styles/globals.css";
import OverlayProgress from "./OverlayProgress";

// Set the default timezone to use on the client
if (typeof window !== "undefined") {
  try {
    const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    Settings.defaultZone = timeZone;
  } catch (e) {
    console.error(e);
  }
}

function App({ Component, pageProps }: AppPropsWithLayout) {
  const apolloClient = useApollo(pageProps);
  const { me, cookieHeader } = pageProps;
  const getLayout =
    Component.getLayout ??
    ((page) => <DefaultLayout pageProps={pageProps}>{page}</DefaultLayout>);

  const cookies = useMemo(
    () => (cookieHeader ? new Cookies(cookieHeader) : undefined),
    [cookieHeader],
  );

  Settings.defaultLocale = me?.user?.language ?? "en";
  useEffect(() => {
    setUser(me?.user ? { email: me.user.email, id: me.user.id } : null);
  }, [me]);
  return (
    <ErrorBoundary>
      <CookiesProvider cookies={cookies}>
        <MeProvider me={me}>
          <NavigationProgress color="#002C5F" height={3} />
          <OverlayProgress />
          <ApolloProvider client={apolloClient}>
            <Head>
              <meta
                name="viewport"
                content="width=device-width, initial-scale=1"
              />
              <meta name="description" content="" />
            </Head>
            {getLayout(<Component {...pageProps} />, pageProps)}
            <ToastContainer
              pauseOnFocusLoss={false}
              pauseOnHover={false}
              hideProgressBar={true}
            />
          </ApolloProvider>
        </MeProvider>
      </CookiesProvider>
    </ErrorBoundary>
  );
}

export default appWithTranslation(App);
