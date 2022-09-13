import {
  ApolloClient,
  ApolloLink,
  InMemoryCache,
  NormalizedCacheObject,
  createHttpLink,
  InMemoryCacheConfig,
} from "@apollo/client";
import { onError } from "@apollo/link-error";
import merge from "deepmerge";
import { IncomingHttpHeaders } from "http";
import fetch from "isomorphic-unfetch";
import isEqual from "lodash/isEqual";
import type { AppProps } from "next/app";
import { useMemo } from "react";
import getConfig from "next/config";

const APOLLO_STATE_PROP_NAME = "__APOLLO_STATE__";

export type CustomApolloClient = ApolloClient<NormalizedCacheObject>;

let apolloClient: CustomApolloClient | undefined;

const { publicRuntimeConfig } = getConfig();

const CACHE_CONFIG: InMemoryCacheConfig = {
  // possibleTypes must be provided to cache correctly unions and interfaces
  // https://www.apollographql.com/docs/react/data/fragments/#using-fragments-with-unions-and-interfaces
  possibleTypes: {
    CollectionElement: [
      "DHIS2DataElementCollectionElement",
      "S3ObjectCollectionElement",
    ],
  },
  typePolicies: {
    Team: {
      merge: true,
      fields: {
        permissions: {
          merge: true,
        },
      },
    },
    DAGRun: {
      merge: true,
    },
    User: {
      merge: true,
    },
    Country: {
      // Country code are unique (at least it should). Let's use that for the cache key
      keyFields: ["code"],
    },
    CatalogEntryType: {
      merge: true,
    },
  },
};

const createApolloClient = (headers: IncomingHttpHeaders | null = null) => {
  const enhancedFetch = (url: RequestInfo, init: RequestInit) => {
    return fetch(url, {
      ...init,
      headers: {
        ...init.headers,
        cookie: headers?.cookie ?? "",
        accept: "application/json",
      },
    });
  };

  const link = ApolloLink.from([
    onError(({ graphQLErrors, networkError }) => {
      if (graphQLErrors) {
        graphQLErrors.forEach(({ message, locations, path }) =>
          console.error(
            `[GraphQL error]: Message: ${message}, Location: ${JSON.stringify(
              locations
            )}, Path: ${path}`
          )
        );
      }
      if (networkError) {
        console.error(
          `[Network error]: ${networkError}. Backend is unreachable. Is it running?`
        );
      }
    }),

    createHttpLink({
      uri: (operation) =>
        operation.operationName
          ? `${publicRuntimeConfig.GRAPHQL_ENDPOINT}${operation.operationName}/`
          : publicRuntimeConfig.GRAPHQL_ENDPOINT,
      fetch: enhancedFetch,
      credentials: "include",
      fetchOptions: {
        mode: "cors",
      },
    }),
  ]);

  const cache = new InMemoryCache(CACHE_CONFIG);

  return new ApolloClient({
    ssrMode: typeof window === "undefined",
    ssrForceFetchDelay: 100, // in milliseconds
    link,
    cache,
  });
};

type InitialState = NormalizedCacheObject | undefined;
export interface GetApolloClient {
  headers?: IncomingHttpHeaders | null;
  initialState?: InitialState | null;
}

export const getApolloClient = (
  { headers, initialState }: GetApolloClient = {
    headers: null,
    initialState: null,
  }
) => {
  const client = apolloClient ?? createApolloClient(headers);

  // If your page has Next.js data fetching methods that use Apollo Client, the initial state
  // get hydrated here
  if (initialState) {
    // Get existing cache, loaded during client side data fetching
    const existingCache = client.extract();

    // Merge the existing cache into data passed from getStaticProps/getServerSideProps
    const data = merge(initialState, existingCache, {
      // combine arrays using object equality (like in sets)
      arrayMerge: (destinationArray, sourceArray) => [
        ...sourceArray,
        ...destinationArray.filter((d) =>
          sourceArray.every((s) => !isEqual(d, s))
        ),
      ],
    });
    // Restore the cache with the merged data
    client.cache.restore(data);
  }

  // For SSG and SSR always create a new Apollo Client
  if (typeof window === "undefined") {
    return client;
  } else if (!apolloClient) {
    // Create the Apollo Client once in the client
    apolloClient = client;
  }

  return client;
};

export const addApolloState = (client: ApolloClient<NormalizedCacheObject>) => {
  return { props: { [APOLLO_STATE_PROP_NAME]: client.cache.extract() } };
};

export function useApollo(
  pageProps: AppProps<{ [key: string]: any }>["pageProps"]
) {
  const state = pageProps[APOLLO_STATE_PROP_NAME];
  const client = useMemo(
    () => getApolloClient({ initialState: state }),
    [state]
  );
  return client;
}
