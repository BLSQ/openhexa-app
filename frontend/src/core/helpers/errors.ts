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