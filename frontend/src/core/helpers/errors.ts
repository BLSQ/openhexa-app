import { ApolloError, type ServerError } from "@apollo/client";

const isServerError = (error: unknown): error is ServerError =>
  error instanceof Error && error.name === "ServerError";

export type RequestTooLargeError = ApolloError & {
  networkError: ServerError & { statusCode: 413 };
};

export const isRequestTooLargeError = (
  error: unknown,
): error is RequestTooLargeError =>
  error instanceof ApolloError &&
  isServerError(error.networkError) &&
  error.networkError.statusCode === 413;

// Coarse cause of a transport-level failure, i.e. one that prevented us from
// getting a well-formed response at all (as opposed to a response that reports
// its own domain error). Callers own the user-facing copy for each kind.
export type TransportErrorKind = "too-large" | "connection" | "server";

export const classifyTransportError = (
  error: ApolloError,
): TransportErrorKind => {
  if (isRequestTooLargeError(error)) {
    return "too-large";
  }
  // A network error with no HTTP status never reached the server (offline,
  // DNS/TLS failure, aborted request); one carrying a status is a server fault.
  const statusCode = (error.networkError as { statusCode?: number } | null)
    ?.statusCode;
  if (error.networkError && statusCode === undefined) {
    return "connection";
  }
  return "server";
};
