import type { AppProps } from "next/app";
import type { NextPage } from "next";
import type { ReactElement } from "react";
import { CustomApolloClient } from "./apollo";

export type NextPageWithLayout<T = any> = NextPage<T> & {
  getLayout?: (page: ReactElement) => ReactElement;
};

export type NextPageWithFragments<T = any> = NextPage<T> & {
  fragments: { [key: string]: any };
};

export type NextPageWithPrefetch<T = any> = NextPage<T> & {
  prefetch: (
    client: CustomApolloClient,
    options: { [key: string]: any }
  ) => Promise<void> | void;
};

export type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};

export type Unpacked<T> = T extends (infer U)[] ? U : T;

export type PromiseReturnType<T> = T extends Promise<infer Return> ? Return : T;

export function isTruthy<T>(value: T): value is NonNullable<T> {
  return value != undefined;
}
