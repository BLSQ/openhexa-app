import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MockedResponse } from "@apollo/client/testing";
import { toast } from "react-toastify";
import { TestApp } from "core/helpers/testutils";
import { UpdateWebappDocument } from "webapps/graphql/mutations.generated";
import { WebappOperationScope } from "graphql/types";
import WebappApiAccess from "./WebappApiAccess";

jest.mock("react-toastify", () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
}));

const webapp = {
  __typename: "Webapp" as const,
  id: "1",
  serveUrl: "https://my-app.example/",
  allowedOperations: [WebappOperationScope.PipelinesRead],
  permissions: { __typename: "WebappPermissions" as const, update: true },
};

describe("WebappApiAccess", () => {
  it("shows the endpoint and the saved scopes read-only", () => {
    render(
      <TestApp mocks={[]}>
        <WebappApiAccess webapp={webapp} />
      </TestApp>,
    );

    expect(
      screen.getByText("https://my-app.example/graphql/"),
    ).toBeInTheDocument();

    const readScope = screen.getByRole("switch", { name: "Read pipelines" });
    expect(readScope).toBeChecked();
    expect(readScope).toBeDisabled();

    const runScope = screen.getByRole("switch", { name: "Run pipelines" });
    expect(runScope).not.toBeChecked();
    expect(runScope).toBeDisabled();
  });

  it("saves the updated scopes", async () => {
    const mocks: MockedResponse[] = [
      {
        request: {
          query: UpdateWebappDocument,
          variables: {
            input: {
              id: "1",
              allowedOperations: [
                WebappOperationScope.PipelinesRead,
                WebappOperationScope.PipelinesRun,
              ],
            },
          },
        },
        result: {
          data: { updateWebapp: { success: true, errors: [], webapp: null } },
        },
      },
    ];

    render(
      <TestApp mocks={mocks}>
        <WebappApiAccess webapp={webapp} />
      </TestApp>,
    );

    fireEvent.click(screen.getByRole("button", { name: "Edit" }));

    const runScope = screen.getByRole("switch", { name: "Run pipelines" });
    expect(runScope).not.toBeDisabled();
    fireEvent.click(runScope);

    fireEvent.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "API access updated successfully",
      );
    });
  });

  it("offers the database scope and saves it", async () => {
    const mocks: MockedResponse[] = [
      {
        request: {
          query: UpdateWebappDocument,
          variables: {
            input: {
              id: "1",
              allowedOperations: [
                WebappOperationScope.PipelinesRead,
                WebappOperationScope.DatabaseRead,
              ],
            },
          },
        },
        result: {
          data: { updateWebapp: { success: true, errors: [], webapp: null } },
        },
      },
    ];

    render(
      <TestApp mocks={mocks}>
        <WebappApiAccess webapp={webapp} />
      </TestApp>,
    );

    fireEvent.click(screen.getByRole("button", { name: "Edit" }));
    fireEvent.click(screen.getByRole("switch", { name: "Read database" }));
    fireEvent.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "API access updated successfully",
      );
    });
  });

  it("does not offer write scopes to a web app that does not have them", () => {
    render(
      <TestApp mocks={[]}>
        <WebappApiAccess webapp={webapp} />
      </TestApp>,
    );

    expect(
      screen.queryByRole("switch", { name: "Write files" }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("switch", { name: "Write datasets" }),
    ).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Edit" }));

    expect(
      screen.queryByRole("switch", { name: "Write files" }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("switch", { name: "Write datasets" }),
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("switch", { name: "Read files" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("switch", { name: "Read datasets" }),
    ).toBeInTheDocument();
  });

  it("keeps write scopes editable for a web app that already has them", async () => {
    const mocks: MockedResponse[] = [
      {
        request: {
          query: UpdateWebappDocument,
          variables: {
            input: {
              id: "1",
              allowedOperations: [WebappOperationScope.DatasetsWrite],
            },
          },
        },
        result: {
          data: { updateWebapp: { success: true, errors: [], webapp: null } },
        },
      },
    ];

    render(
      <TestApp mocks={mocks}>
        <WebappApiAccess
          webapp={{
            ...webapp,
            allowedOperations: [
              WebappOperationScope.FilesWrite,
              WebappOperationScope.DatasetsWrite,
            ],
          }}
        />
      </TestApp>,
    );

    expect(screen.getByRole("switch", { name: "Write files" })).toBeChecked();
    expect(
      screen.getByRole("switch", { name: "Write datasets" }),
    ).toBeChecked();

    fireEvent.click(screen.getByRole("button", { name: "Edit" }));
    fireEvent.click(screen.getByRole("switch", { name: "Write files" }));
    fireEvent.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "API access updated successfully",
      );
    });
  });

  it("does not allow editing without update permission", () => {
    render(
      <TestApp mocks={[]}>
        <WebappApiAccess
          webapp={{
            ...webapp,
            permissions: { __typename: "WebappPermissions", update: false },
          }}
        />
      </TestApp>,
    );

    expect(
      screen.queryByRole("button", { name: "Edit" }),
    ).not.toBeInTheDocument();
  });
});
