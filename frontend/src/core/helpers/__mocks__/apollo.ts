const client = {
  query: jest.fn(),
  mutate: jest.fn(),
};

export type GetApolloMock = {
  query: jest.Mock;
  mutate: jest.Mock;
};

export const getApolloClient = jest.fn(() => client);

getApolloClient.query = client.query;
getApolloClient.mutate = client.mutate;
