import {
  ApolloClient,
  ApolloLink,
  createHttpLink,
  InMemoryCache,
  InMemoryCacheConfig,
  NormalizedCacheObject,
} from "@apollo/client";
import { onError } from "@apollo/link-error";
import merge from "deepmerge";
import { IncomingHttpHeaders } from "http";
import fetch from "isomorphic-unfetch";
import isEqual from "lodash/isEqual";
import type { AppProps } from "next/app";
import { useMemo } from "react";
import getConfig from "next/config";

const { publicRuntimeConfig } = getConfig();
const APOLLO_STATE_PROP_NAME = "__APOLLO_STATE__";

export type CustomApolloClient = ApolloClient<NormalizedCacheObject>;

let apolloClient: CustomApolloClient | undefined;

const CACHE_CONFIG: InMemoryCacheConfig = {
  // possibleTypes must be provided to cache correctly unions and interfaces
  // https://www.apollographql.com/docs/react/data/fragments/#using-fragments-with-unions-and-interfaces
  possibleTypes: {},
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
    Dataset: {
      merge: true,
    },
    Country: {
      // Country code are unique (at least it should). Let's use that for the cache key
      keyFields: ["code"],
    },
    CatalogEntryType: {
      merge: true,
    },
    Workspace: {
      merge: true,
      keyFields: ["slug"],
    },
    WorkspacePermissions: {
      merge: true,
    },

    DatasetPermissions: {
      merge: true,
    },
    DatabaseTable: {
      merge: true,
    },
    Bucket: {
      merge: true,
    },
    BucketObject: {
      merge: true,
      keyFields: ["key"],
    },

    Pipeline: {
      merge: true,
    },
  },
};

const createApolloClient = (headers: IncomingHttpHeaders | null = null) => {
  const enhancedFetch = (input: RequestInfo | URL, init?: RequestInit) => {
    if (typeof init === "undefined") {
      init = {};
    }
    return fetch(input, {
      ...init,
      headers: {
        ...init.headers,
        cookie: headers?.cookie ?? "",
        accept: "application/json",
      },
    });
  };

  const ssrMode = typeof window === "undefined";
  const link = ApolloLink.from([
    onError(({ graphQLErrors, networkError }) => {
      if (graphQLErrors) {
        graphQLErrors.forEach(({ message, locations, path, extensions }) => {
          console.error(
            `[GraphQL error]: Message: ${message}, Location: ${JSON.stringify(
              locations,
            )}, Path: ${path}, Extension Code: ${extensions?.code}`,
          );
        });
      }
      if (networkError) {
        console.error(
          `[Network error]: ${networkError}. Backend is unreachable. Is it running?`,
        );
      }
    }),
    createHttpLink({
      uri: (operation) => {
        let apiUrl =
          typeof window === "undefined"
            ? `${publicRuntimeConfig.OPENHEXA_BACKEND_URL}/graphql/`
            : "/graphql/";
        if (operation.operationName) {
          apiUrl += `${operation.operationName}/`;
        }
        return apiUrl;
      },
      fetch: enhancedFetch,
      credentials: "include",
    }),
  ]);

  const cache = new InMemoryCache(CACHE_CONFIG);

  return new ApolloClient({
    ssrMode,
    ssrForceFetchDelay: 100, // in milliseconds
    link,
    cache,
    defaultOptions: {
      watchQuery: {
        fetchPolicy: "cache-and-network",
      },
    },
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
  },
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
          sourceArray.every((s) => !isEqual(d, s)),
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
  pageProps: AppProps<{ [key: string]: any }>["pageProps"],
) {
  const state = pageProps[APOLLO_STATE_PROP_NAME];
  const client = useMemo(
    () => getApolloClient({ initialState: state }),
    [state],
  );
  return client;
}
