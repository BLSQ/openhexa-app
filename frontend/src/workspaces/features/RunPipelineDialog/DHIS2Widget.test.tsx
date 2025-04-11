import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import { DHIS2Widget, GET_CONNECTION_METADATA } from "./DHIS2Widget";

jest.mock("core/hooks/useDebounce", () => ({
  __esModule: true,
  default: jest.fn((value) => value),
}));

const generateMockedParameterField = (multiple = false) => ({
  parameter: {
    name: "Test Parameter",
    code: "test_param",
    widget: "DHIS2_DATASETS",
    multiple: true,
    type: "str",
    connection: "test_connection",
    required: true,
  },
  widget: "DHIS2_DATASETS",
  form: {
    formData: { test_connection: "mock_connection_slug", test_param: null },
    setFieldValue: jest.fn(),
  },
  workspaceSlug: "mock_workspace",
});

describe("DHIS2Widget", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the component correctly", async () => {
    const parameterField = generateMockedParameterField();

    const { debug } = render(
      <TestApp
        mocks={[
          {
            request: {
              query: GET_CONNECTION_METADATA,
              variables: {
                workspaceSlug: "mock_workspace",
                connectionSlug: "mock_connection_slug",
                type: "ORG_UNIT_LEVELS",
                filters: [],
                perPage: 15,
                page: 1,
              },
            },
            result: {
              data: {
                connectionBySlug: {
                  queryMetadata: { items: [], totalItems: 0 },
                },
              },
            },
          },
        ]}
      >
        <DHIS2Widget {...parameterField} />
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
                type: "ORG_UNIT_LEVELS",
                filters: [],
                perPage: 15,
                page: 1,
              },
            },
            result: {
              data: {
                connectionBySlug: {
                  queryMetadata: {
                    items: [
                      { id: "1", label: "Item 1" },
                      { id: "2", label: "Item 2" },
                    ],
                    totalItems: 2,
                  },
                },
              },
            },
          },
        ]}
      >
        <DHIS2Widget {...pipeline} />
      </TestApp>,
    );
    const user = userEvent.setup();
    await user.click(await screen.findByTestId("combobox-button"));
    waitFor(() => {
      const options = screen.queryAllByTestId("combobox-options");
      expect(options.length).toBe(2);
    });
  });

  it("updates selected value in single select mode", async () => {
    const pipeline = generateMockedParameterField(false);

    const { container } = render(
      <TestApp
        mocks={[
          {
            request: {
              query: GET_CONNECTION_METADATA,
              variables: {
                workspaceSlug: "mock_workspace",
                connectionSlug: "mock_connection_slug",
                type: "ORG_UNIT_LEVELS",
                filters: [],
                perPage: 15,
                page: 1,
              },
            },
            result: {
              data: {
                connectionBySlug: {
                  queryMetadata: {
                    items: [
                      { id: "1", label: "Item 1" },
                      { id: "2", label: "Item 2" },
                    ],
                    totalItems: 2,
                  },
                },
              },
            },
          },
        ]}
      >
        <DHIS2Widget {...pipeline} />
      </TestApp>,
    );
    const user = userEvent.setup();
    await user.click(await screen.findByTestId("combobox-button"));
    waitFor(async () => {
      const options = screen.queryAllByTestId("combobox-options");
      expect(options.length).toBe(1);
      await user.click(options[0]);
    });
    waitFor(() => {
      expect(pipeline.form.setFieldValue).toHaveBeenCalledWith(
        "test_param",
        "1",
      );
    });
  });
});
