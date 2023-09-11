import { useCallback, useEffect } from "react";

type EventElement = HTMLElement | Window;

export const useEmitter = <T = any>(
  eventName: string,
  element?: EventElement,
) => {
  const callEvent = useCallback(
    (data?: T) => {
      const event = new CustomEvent(eventName, { detail: data });

      (element || window).dispatchEvent(event);
    },
    [eventName, element],
  );

  return callEvent;
};

export const useListener = <T = any>(
  eventName: string,
  onEvent: (e: CustomEvent<T>) => void,
  element?: EventElement,
  options: boolean | AddEventListenerOptions = {},
) => {
  useEffect(() => {
    if (typeof onEvent === "function") {
      const handleSignal = (e: Event) => {
        onEvent(e as CustomEvent<T>);
      };

      (element || window).addEventListener(eventName, handleSignal, options);

      return () =>
        (element || window).removeEventListener(
          eventName,
          handleSignal,
          options,
        );
    }
  }, [element, eventName, onEvent, options]);
};
