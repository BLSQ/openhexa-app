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

function App({ Component, pageProps }: AppPropsWithLayout) {
  const apolloClient = useApollo(pageProps);

  const getLayout =
    Component.getLayout ??
    ((page) => <Layout pageProps={pageProps}>{page}</Layout>);

  useEffect(() => {
    Sentry.setUser(
      pageProps.user
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
