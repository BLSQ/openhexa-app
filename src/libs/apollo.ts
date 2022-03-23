import {
  ApolloClient,
  ApolloLink,
  InMemoryCache,
  NormalizedCacheObject,
  createHttpLink,
} from "@apollo/client";
import { onError } from "@apollo/link-error";
import merge from "deepmerge";
import { IncomingHttpHeaders } from "http";
import fetch from "isomorphic-unfetch";
import isEqual from "lodash/isEqual";
import type { AppProps } from "next/app";
import { useMemo } from "react";

const APOLLO_STATE_PROP_NAME = "__APOLLO_STATE__";

export type CustomApolloClient = ApolloClient<NormalizedCacheObject>;

let apolloClient: CustomApolloClient | undefined;

const createApolloClient = (headers: IncomingHttpHeaders | null = null) => {
  const enhancedFetch = (url: RequestInfo, init: RequestInit) => {
    if (process.env.NODE_ENV === "development") {
      const body = JSON.parse(init.body as string);
      console.log(`Fetch ${url}${body.operationName}`);
    }
    return fetch(url, {
      ...init,
      headers: {
        ...init.headers,
        cookie: headers?.cookie ?? "",
      },
    }).then((resp) => resp);
  };
  return new ApolloClient({
    ssrMode: typeof window === "undefined",
    link: ApolloLink.from([
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
        uri: process.env.NEXT_PUBLIC_GRAPHQL_ENDPOINT,
        fetch: enhancedFetch,
        credentials: "include",
        fetchOptions: {
          mode: "cors",
        },
      }),
    ]),
    cache: new InMemoryCache({
      // possibleTypes must be provided to cache correctly unions and interfaces
      // https://www.apollographql.com/docs/react/data/fragments/#using-fragments-with-unions-and-interfaces
      possibleTypes: {
        AccessmodAnalysis: [
          "AccessmodGeographicCoverageAnalysis",
          "AccessmodAccessibilityAnalysis",
        ],
      },
      typePolicies: {
        Country: {
          // Country code are unique (at least it should). Let's use that for the cache key
          keyFields: false,
        },
      },
    }),
  });
};

type InitialState = NormalizedCacheObject | undefined;
interface IGetApolloClient {
  headers?: IncomingHttpHeaders | null;
  initialState?: InitialState | null;
}

export const getApolloClient = (
  { headers, initialState }: IGetApolloClient = {
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

export function useApollo(pageProps: AppProps["pageProps"]) {
  const state = pageProps[APOLLO_STATE_PROP_NAME];
  const client = useMemo(
    () => getApolloClient({ initialState: state }),
    [state]
  );
  return client;
}
