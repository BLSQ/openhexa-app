import { useCookies } from "react-cookie";
import { CookieSetOptions } from "universal-cookie";

const ONE_YEAR_IN_SECONDS = 60 * 60 * 24 * 365;

const DEFAULT_OPTIONS: CookieSetOptions = {
  path: "/",
  maxAge: ONE_YEAR_IN_SECONDS,
};

interface UseCookieStateOptions<T> {
  name: string;
  defaultValue: T;
  options?: CookieSetOptions;
}

export default function useCookieState<T>({
  name,
  defaultValue,
  options,
}: UseCookieStateOptions<T>) {
  const [cookies, setCookie] = useCookies([name]);

  const value: T = cookies[name] ?? defaultValue;

  const setValue = (newValue: T) => {
    setCookie(name, newValue, { ...DEFAULT_OPTIONS, ...options });
  };

  return [value, setValue] as const;
}
