import { ApolloProvider } from "@apollo/client";
import { useApollo } from "core/helpers/apollo";
import DefaultLayout from "core/layouts/default";
import { AppPropsWithLayout } from "core/helpers/types";
import { appWithTranslation } from "next-i18next";
import NavigationProgress from "nextjs-progressbar";
import "../styles/globals.css";
import AlertManager from "core/components/AlertManager";
import { useEffect } from "react";
import { setUser } from "@sentry/nextjs";
import ErrorBoundary from "core/components/ErrorBoundary/ErrorBoundary";
import { Settings } from "luxon";
import Head from "next/head";
// Set the default timezone to use on the client
import { MeProvider } from "identity/hooks/useMe";
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
  const { me } = pageProps;
  const getLayout =
    Component.getLayout ??
    ((page) => <DefaultLayout pageProps={pageProps}>{page}</DefaultLayout>);

  Settings.defaultLocale = me?.user?.language ?? "en";
  useEffect(() => {
    setUser(me?.user ? { email: me.user.email, id: me.user.id } : null);
  }, [me]);
  return (
    <ErrorBoundary>
      <MeProvider me={me}>
        <NavigationProgress color="#002C5F" height={3} />
        <ApolloProvider client={apolloClient}>
          <Head>
            <meta
              name="viewport"
              content="width=device-width, initial-scale=1"
            />
            <meta name="description" content="" />
          </Head>
          {getLayout(<Component {...pageProps} />, pageProps)}
          <AlertManager />
        </ApolloProvider>
      </MeProvider>
    </ErrorBoundary>
  );
}

export default appWithTranslation(App);
