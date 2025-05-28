import {render, screen, waitFor} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {TestApp} from "core/helpers/testutils";
import {IASOWidget, GET_CONNECTION_METADATA} from "./IASOWidget";

jest.mock("core/hooks/useDebounce", () => ({
  __esModule: true,
  default: jest.fn((value) => value),
}));

const generateMockedParameterField = (multiple = false) => ({
  parameter: {
    name: "Test Parameter",
    code: "test_param",
    widget: "IASO_PROJECTS",
    multiple,
    type: "str",
    connection: "test_connection",
    required: true,
  },
  widget: "IASO_PROJECTS",
  form: {
    formData: {test_connection: "mock_connection_slug", test_param: null},
    setFieldValue: jest.fn(),
  },
  workspaceSlug: "mock_workspace",
});

describe("IASOWidget", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the component correctly", async () => {
    const parameterField = generateMockedParameterField();

    render(
      <TestApp
        mocks={[
          {
            request: {
              query: GET_CONNECTION_METADATA,
              variables: {
                workspaceSlug: "mock_workspace",
                connectionSlug: "mock_connection_slug",
                type: "IASO_PROJECTS",
                search: null,
                filters: [],
                perPage: 15,
                page: 1,
              },
            },
            result: {
              data: {
                connectionBySlug: {
                  __typename: "IASOConnection",
                  queryMetadata: {items: [], totalItems: 0, pageNumber: 1},
                },
              },
            },
          },
        ]}
      >
        <IASOWidget {...parameterField} />
      </TestApp>,
    );

    expect(screen.getByPlaceholderText("Select options")).toBeInTheDocument();
    expect(screen.getByRole("combobox")).not.toHaveAttribute("disabled");
  });

  it("fetches data when connection is provided", async () => {
    const pipeline = generateMockedParameterField(true);
    render(
      <TestApp
        mocks={[
          {
            request: {
              query: GET_CONNECTION_METADATA,
              variables: {
                workspaceSlug: "mock_workspace",
                connectionSlug: "mock_connection_slug",
                type: "IASO_PROJECTS",
                search: null,
                filters: [],
                perPage: 15,
                page: 1,
              },
            },
            result: {
              data: {
                connectionBySlug: {
                  __typename: "IASOConnection",
                  queryMetadata: {
                    items: [
                      {id: "1", label: "Project 1"},
                      {id: "2", label: "Project 2"},
                    ],
                    totalItems: 2,
                    pageNumber: 1,
                  },
                },
              },
            },
          },
        ]}
      >
        <IASOWidget {...pipeline} />
      </TestApp>,
    );

    const user = userEvent.setup();
    await user.click(await screen.findByTestId("combobox-button"));

    await waitFor(() => {
      expect(screen.getByText("Project 1")).toBeInTheDocument();
      expect(screen.getByText("Project 2")).toBeInTheDocument();
    });
  });

  it("updates selected value in single select mode", async () => {
    const pipeline = generateMockedParameterField(false);

    render(
      <TestApp
        mocks={[
          {
            request: {
              query: GET_CONNECTION_METADATA,
              variables: {
                workspaceSlug: "mock_workspace",
                connectionSlug: "mock_connection_slug",
                type: "IASO_PROJECTS",
                search: null,
                filters: [],
                perPage: 15,
                page: 1,
              },
            },
            result: {
              data: {
                connectionBySlug: {
                  __typename: "IASOConnection",
                  queryMetadata: {
                    items: [
                      {id: "1", label: "Project 1"},
                      {id: "2", label: "Project 2"},
                    ],
                    totalItems: 2,
                    pageNumber: 1,
                  },
                },
              },
            },
          },
        ]}
      >
        <IASOWidget {...pipeline} />
      </TestApp>,
    );

    const user = userEvent.setup();
    await user.click(await screen.findByTestId("combobox-button"));
    await waitFor(() => screen.getByText("Project 1"));
    await user.click(screen.getByText("Project 1"));

    await waitFor(() => {
      expect(pipeline.form.setFieldValue).toHaveBeenCalledWith(
        "test_param",
        "1",
      );
    });
  });
});
