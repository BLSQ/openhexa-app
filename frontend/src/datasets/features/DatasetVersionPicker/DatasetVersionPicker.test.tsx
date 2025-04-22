import { useQuery } from "@apollo/client";
import { faker } from "@faker-js/faker";
import "@testing-library/jest-dom";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { DateTime } from "luxon";
import DatasetVersionPicker from "./DatasetVersionPicker";

import { mockIntersectionObserver } from "jsdom-testing-mocks";

jest.mock("@apollo/client", () => ({
  __esModule: true,
  useQuery: jest.fn(),
  gql: jest.fn(() => "GQL"),
}));

const intersectionObserver = mockIntersectionObserver();

const useQueryMock = useQuery as jest.Mock;

const createMockData = (totalItems: number, itemsPerPage: number) => ({
  dataset: {
    versions: {
      totalItems,
      items: Array.from({ length: itemsPerPage }, () => ({
        id: faker.string.uuid(),
        name: faker.lorem.words(2),
        createdAt: DateTime.now().toISO(),
      })),
    },
  },
});

describe("DatasetVersionPicker component", () => {
  it("pull additional data when scrolling to the last element", async () => {
    const user = userEvent.setup();
    const dataset = { id: faker.string.uuid() };
    const version = null;
    useQueryMock.mockReturnValue({
      loading: false,
      data: createMockData(20, 15),
    });

    render(
      <DatasetVersionPicker
        onChange={() => {}}
        dataset={dataset}
        version={version}
      />,
    );

    const button = screen.getByRole("button");
    await user.click(button);

    expect(screen.queryAllByRole("option")).toHaveLength(15);
    useQueryMock.mockReturnValue({
      loading: false,
      data: createMockData(20, 20),
    });

    intersectionObserver.enterNode(
      screen.getByTestId("intersection-observer-wrapper"),
    );

    await waitFor(() => {
      expect(screen.queryAllByRole("option").length).toBe(20);
    });
  });
});
