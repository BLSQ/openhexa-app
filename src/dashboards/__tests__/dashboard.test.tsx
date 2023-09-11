import { render, screen } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import { DashboardPageDocument } from "dashboards/graphql/queries.generated";
import { DateTime, Settings } from "luxon";
import DashboardPage from "pages";

describe("Dashboard", () => {
  it("renders the dashboards' page", async () => {
    (Settings.now as jest.Mock).mockReturnValue(
      DateTime.fromObject({ year: 2022, month: 10, day: 22 }).toMillis(),
    );
    const graphqlMocks = [
      {
        request: {
          query: DashboardPageDocument,
        },
        result: {
          data: {
            totalNotebooks: 0,
            catalog: {
              totalItems: 6,
            },
            dags: {
              totalItems: 0,
            },
            lastActivities: [
              {
                description: "All datasources are up to date!",
                occurredAt: "2022-11-09T00:00:39.651Z",
                url: "/catalog/",
                status: "SUCCESS",
              },
            ],
          },
        },
      },
    ];

    const { container } = render(
      <TestApp mocks={graphqlMocks}>
        <DashboardPage />
      </TestApp>,
    );
    const elm = await screen.findByText("Overview");
    expect(elm).toBeInTheDocument();
    expect(container).toMatchSnapshot();
  });
});
