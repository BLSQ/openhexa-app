import type { AppProps } from "next/app";
import type { NextPage } from "next";
import type { FC, ReactElement } from "react";
import { CustomApolloClient } from "./apollo";
import { DocumentNode } from "graphql";

export type NextPageWithLayout<PP extends PageProps = any> = NextPage<PP> & {
  getLayout?: (page: ReactElement, pageProps: PP) => ReactElement;
};

export interface ApolloComponent<P = {}> extends FC<P> {
  fragments: { [key: string]: DocumentNode };
}

export type NextPageWithFragments<T = any> = NextPage<T> & {
  fragments: { [key: string]: any };
};

export type NextPageWithPrefetch<T = any> = NextPage<T> & {
  prefetch: (
    client: CustomApolloClient,
    options: { [key: string]: any },
  ) => Promise<void> | void;
};

type PageProps = { [key: string]: any };

export type AppPropsWithLayout<P extends PageProps = any> = AppProps<P> & {
  Component: NextPageWithLayout<P>;
};

export type Unpacked<T> = T extends (infer U)[] ? U : T;

export type PromiseReturnType<T> = T extends Promise<infer Return> ? Return : T;

export function isTruthy<T>(value: T): value is NonNullable<T> {
  return value != undefined;
}
