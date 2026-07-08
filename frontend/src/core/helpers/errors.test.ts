import { ApolloError } from "@apollo/client";
import { classifyTransportError } from "./errors";

const serverNetworkError = (statusCode: number) => {
  const error = new Error("Server responded with an error") as Error & {
    statusCode: number;
  };
  error.name = "ServerError";
  error.statusCode = statusCode;
  return error;
};

describe("classifyTransportError", () => {
  it("classifies a 413 as too-large", () => {
    expect(
      classifyTransportError(
        new ApolloError({ networkError: serverNetworkError(413) }),
      ),
    ).toBe("too-large");
  });

  it("classifies a statusless network error as a connection problem", () => {
    expect(
      classifyTransportError(
        new ApolloError({ networkError: new Error("Failed to fetch") }),
      ),
    ).toBe("connection");
  });

  it("classifies a network error carrying an HTTP status as a server fault", () => {
    expect(
      classifyTransportError(
        new ApolloError({ networkError: serverNetworkError(500) }),
      ),
    ).toBe("server");
  });

  it("classifies a GraphQL error as a server fault", () => {
    expect(
      classifyTransportError(
        new ApolloError({ graphQLErrors: [{ message: "boom" } as any] }),
      ),
    ).toBe("server");
  });
});
