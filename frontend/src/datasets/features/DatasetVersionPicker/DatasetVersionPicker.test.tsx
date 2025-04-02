import { useQuery } from "@apollo/client";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { faker } from "@faker-js/faker";
import DatasetVersionPicker from "./DatasetVersionPicker";
import "@testing-library/jest-dom";
import { DateTime } from "luxon";
import useIntersectionObserver from "core/hooks/useIntersectionObserver";

jest.mock("@apollo/client", () => ({
  __esModule: true,
  useQuery: jest.fn(),
  gql: jest.fn(() => "GQL"),
}));

jest.mock("core/hooks/useIntersectionObserver");

const useQueryMock = useQuery as jest.Mock;
const useIntersectionObserverMock = useIntersectionObserver as jest.Mock;

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
    const dataset = { id: faker.string.uuid() };
    const version = null;

    useQueryMock.mockReturnValue({
      loading: false,
      data: createMockData(20, 15),
    });

    let isIntersecting = false;
    useIntersectionObserverMock.mockImplementation(() => ({
      isIntersecting,
    }));

    render(
      <DatasetVersionPicker
        onChange={() => {}}
        dataset={dataset}
        version={version}
      />,
    );

    const button = screen.getByRole("button");
    fireEvent.click(button);

    expect(screen.queryAllByRole("option")).toHaveLength(15);

    useQueryMock.mockReturnValue({
      loading: false,
      data: createMockData(20, 20),
    });

    isIntersecting = true;
    const dropdown = await screen.findByRole("listbox");
    fireEvent.scroll(dropdown, {
      target: { scrollTop: 2000 },
    });

    await waitFor(() => {
      expect(screen.queryAllByRole("option")).toHaveLength(20);
    });
  });
});
