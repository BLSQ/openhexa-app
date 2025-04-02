import { ensureArray } from "core/helpers/array";
import isEqual from "lodash/isEqual";
import { useCallback, useEffect, useState } from "react";
import { useEmitter, useListener } from "./useEmitter";

/**
 * Hook to force data to be re-fetched somewhere else in the application.
 *
 * Example:
 *  const MyComponent = () => {
 *    const clearCache = useCacheKey(["projects","2"])
 *
 *    return <button onClick={clearCache}>Clear the cache</button>
 *  }
 *
 *  const ProjectsComponent = () => {
 *    const {data: projects, refetch} = useQuery(...)
 *    useListener(["projects"], () => refetch())
 *    ...
 *  }
 *
 * @param keys Keys that need to match in order to call the listener
 * @param listener Function that is called when the keys received with the `propagate` call match the one passed in arguments
 * @returns
 *
 */

const useCacheKey = (keys: any | any[], listener?: () => void) => {
  const [cachedKeys, setCachedKeys] = useState(keys);
  const emit = useEmitter("CacheKey");

  useEffect(() => {
    if (!isEqual(keys, cachedKeys)) {
      setCachedKeys(keys);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [keys]);

  useListener<{ keys: string[] }>("CacheKey", (event) => {
    if (!listener) {
      // We may use this hook only to propagate a cache reset (and we cannot call a hook in a conditional statement)
      return;
    }

    const keys = ensureArray(cachedKeys);
    if (keys.length > event.detail.keys.length) {
      return; // Listened keys array is longer (more precise) than the received keys array
    }

    keys.forEach((k, index) => {
      if (k !== event.detail.keys[index]) {
        // Keys are different -> no match
        return;
      }
    });

    // Let's call the listener :)
    listener();
  });

  const propagate = useCallback(() => {
    emit({ keys: ensureArray(cachedKeys) });
  }, [cachedKeys, emit]);

  return propagate;
};

export default useCacheKey;
