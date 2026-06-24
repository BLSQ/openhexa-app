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

    const readScope = screen.getByLabelText(
      "Read pipelines",
    ) as HTMLInputElement;
    expect(readScope.checked).toBe(true);
    expect(readScope.disabled).toBe(true);

    const runScope = screen.getByLabelText("Run pipelines") as HTMLInputElement;
    expect(runScope.checked).toBe(false);
    expect(runScope.disabled).toBe(true);
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

    const runScope = screen.getByLabelText("Run pipelines") as HTMLInputElement;
    expect(runScope.disabled).toBe(false);
    fireEvent.click(runScope);

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
