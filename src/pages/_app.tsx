import Head from "next/head";
import { ApolloProvider } from "@apollo/client";
import { useApollo } from "core/helpers/apollo";
import DefaultLayout from "core/layouts/default";
import { AppPropsWithLayout } from "core/helpers/types";
import { appWithTranslation } from "next-i18next";
import NavigationProgress from "nextjs-progressbar";
import "../styles/globals.css";
import { useEffect } from "react";
import { setUser } from "@sentry/nextjs";
import { Settings } from "luxon";
import { MeProvider } from "identity/hooks/useMe";
import ErrorBoundary from "core/components/ErrorBoundary/ErrorBoundary";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

// Set the default locale & timezone to be used on server and client.
// This should be changed to use the correct lang and tz of the user when it's available.
// Fixes #OPENHEXA-D7 Hydration error
Settings.defaultZone = "Europe/Brussels";

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
          <ToastContainer
            pauseOnFocusLoss={false}
            pauseOnHover={false}
            hideProgressBar={true}
          />
        </ApolloProvider>
      </MeProvider>
    </ErrorBoundary>
  );
}

export default appWithTranslation(App);
