import { useCallback, useState } from "react";

const useToggle = (initialState = false) => {
  // Initialize the state
  const [state, setState] = useState(initialState);

  const toggle = useCallback(() => setState((state) => !state), []);
  const setTrue = useCallback(() => setState(true), []);
  const setFalse = useCallback(() => setState(false), []);

  return [state, { toggle, setTrue, setFalse }] as const;
};

export default useToggle;
