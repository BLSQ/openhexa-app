import { render, screen, waitFor } from "@testing-library/react";
import { DateTime, Settings } from "luxon";
import { TestApp } from "core/helpers/testutils";
import VisualizationsPage from "pages/visualizations";
import VisualizationPage from "pages/visualizations/[visualizationId]";
import {
  VisualizationDocument,
  VisualizationsPageDocument,
} from "visualizations/graphql/queries.generated";

describe("Visualization", () => {
  it("renders the visualizations' page", async () => {
    const graphqlMocks = [
      {
        request: {
          query: VisualizationsPageDocument,
          variables: {
            page: 1,
            perPage: 1,
          },
        },
        result: {
          data: {
            externalDashboards: {
              totalPages: 0,
              totalItems: 0,
              items: [],
            },
          },
        },
      },
    ];

    const { container } = render(
      <TestApp mocks={graphqlMocks}>
        <VisualizationsPage page={1} perPage={1} />
      </TestApp>,
    );
    const elm = await screen.findByText("Visualizations", { selector: "h2" });
    expect(elm).toBeInTheDocument();
    expect(container).toMatchSnapshot();
  });

  it("renders the visualizations' page with data", async () => {
    (Settings.now as jest.Mock).mockReturnValue(
      DateTime.fromObject({ year: 2022, month: 10, day: 22 }).toMillis(),
    );

    const visualizationMock = [
      {
        request: {
          query: VisualizationsPageDocument,
          variables: {
            page: 1,
            perPage: 1,
          },
        },
        result: {
          data: {
            externalDashboards: {
              totalPages: 1,
              totalItems: 1,
              items: [
                {
                  id: "351489ac-5bbe-4ed3-aab9-8155024092b4",
                  name: "Untitled Dashboard",
                  url: "https://coronavirus.data.gov.uk/",
                  pictureUrl:
                    "/visualizations/351489ac-5bbe-4ed3-aab9-8155024092b4/image/",
                  createdAt: "2022-10-21T11:35:42.716Z",
                  updatedAt: "2022-10-21T11:35:42.716Z",
                  countries: [],
                  description: "",
                  tags: [],
                },
              ],
            },
          },
        },
      },
    ];
    const { container } = render(
      <TestApp mocks={visualizationMock}>
        <VisualizationsPage page={1} perPage={1} />
      </TestApp>,
    );

    const elm = await screen.findByText("Visualizations", { selector: "h2" });
    expect(elm).toBeInTheDocument();
    expect(container).toMatchSnapshot();

    expect(await screen.findByText("Untitled Dashboard")).toBeInTheDocument();
  });

  it("renders a visualization info page ", async () => {
    const visualizationMock = [
      {
        request: {
          query: VisualizationDocument,
          variables: {
            id: "351489ac-5bbe-4ed3-aab9-8155024092b4",
          },
        },
        result: {
          data: {
            externalDashboard: {
              id: "351489ac-5bbe-4ed3-aab9-8155024092b4",
              name: "Untitled Dashboard",
              url: "https://coronavirus.data.gov.uk/",
              pictureUrl:
                "/visualizations/351489ac-5bbe-4ed3-aab9-8155024092b4/image/",
              createdAt: "2022-10-21T11:35:42.716Z",
              updatedAt: "2022-10-21T11:35:42.716Z",
              countries: [],
              description: "",
              tags: [],
            },
          },
        },
      },
    ];

    const { container } = render(
      <TestApp mocks={visualizationMock}>
        <VisualizationPage visualizationId="351489ac-5bbe-4ed3-aab9-8155024092b4" />
      </TestApp>,
    );

    const elm = await screen.findByText("https://coronavirus.data.gov.uk/");
    expect(elm).toBeInTheDocument();

    waitFor(() => {
      expect(container).toMatchSnapshot();
    });
  });

  it("renders null as the visualization does not exist", async () => {
    const visualizationMock = [
      {
        request: {
          query: VisualizationDocument,
          variables: {
            id: "151489ac-5bbe-4ed3-aab9-8155024092b4",
          },
        },
        result: {
          data: {
            externalDashboard: null,
          },
        },
      },
    ];

    const { container } = render(
      <TestApp mocks={visualizationMock}>
        <VisualizationPage visualizationId="151489ac-5bbe-4ed3-aab9-8155024092b4" />
      </TestApp>,
    );

    expect(container.firstChild).toBeNull();
    expect(container).toMatchSnapshot();
  });
});
