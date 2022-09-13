import Head from "next/head";
import { ApolloProvider } from "@apollo/client";
import { useApollo } from "core/helpers/apollo";
import Layout from "core/components/Layout";
import { AppPropsWithLayout } from "core/helpers/types";
import { appWithTranslation } from "next-i18next";
import NavigationProgress from "nextjs-progressbar";
import "../styles/globals.css";
import AlertManager from "core/components/AlertManager";
import { useEffect } from "react";
import * as Sentry from "@sentry/nextjs";
import { Settings } from "luxon";

// Set the default locale & timezone to be used on server and client.
// This should be changed to use the correct lang and tz of the user when it's available.
// Fixes #OPENHEXA-D7 Hydration error
Settings.defaultLocale = "en";
Settings.defaultZone = "Europe/Brussels";

function App({ Component, pageProps }: AppPropsWithLayout) {
  const apolloClient = useApollo(pageProps);

  const getLayout =
    Component.getLayout ??
    ((page) => <Layout pageProps={pageProps}>{page}</Layout>);

  useEffect(() => {
    Sentry.setUser(
      pageProps?.user
        ? { email: pageProps.user.email, id: pageProps.user.id }
        : null
    );
  }, [pageProps.user]);
  return (
    <>
      <NavigationProgress color="#002C5F" height={3} />
      <ApolloProvider client={apolloClient}>
        <Head>
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <meta name="description" content="" />
        </Head>
        {getLayout(<Component {...pageProps} />)}
        <AlertManager />
      </ApolloProvider>
    </>
  );
}

export default appWithTranslation(App);
