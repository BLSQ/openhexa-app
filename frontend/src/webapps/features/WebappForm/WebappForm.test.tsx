import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MockedResponse } from "@apollo/client/testing";
import { toast } from "react-toastify";
import { TestApp } from "core/helpers/testutils";
import { WebappType } from "graphql/types";
import { SupersetInstancesDocument } from "webapps/graphql/queries.generated";
import { UpdateWebappDocument } from "webapps/graphql/mutations.generated";
import WebappForm from "./WebappForm";

jest.mock("react-toastify", () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
}));

const workspace = {
  __typename: "Workspace",
  slug: "test-workspace",
  name: "Test Workspace",
  countries: [],
  organization: null,
  permissions: {
    launchNotebookServer: false,
    manageMembers: false,
    update: true,
  },
} as any;

const webapp = {
  __typename: "Webapp",
  id: "webapp-1",
  slug: "test-webapp",
  name: "Test Webapp",
  description: "",
  url: "https://old.example.com",
  previewUrl: null,
  type: WebappType.Iframe,
  icon: null,
  isPublic: false,
  subdomain: "test-webapp",
  serveUrl: "https://test-webapp.apps.openhexa.org",
  source: null,
  permissions: {
    update: true,
    delete: true,
  },
} as any;

const supersetInstancesMock: MockedResponse = {
  request: {
    query: SupersetInstancesDocument,
    variables: { workspaceSlug: "test-workspace" },
  },
  maxUsageCount: Infinity,
  result: { data: { supersetInstances: [] } },
};

describe("WebappForm", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("updates an iframe webapp url without sending a null subdomain", async () => {
    const updateVariables = jest.fn();
    const updateMock: MockedResponse = {
      request: { query: UpdateWebappDocument },
      variableMatcher: (variables) => {
        updateVariables(variables);
        return true;
      },
      result: {
        data: {
          updateWebapp: {
            __typename: "UpdateWebappResult",
            success: true,
            errors: [],
            webapp: {
              __typename: "Webapp",
              id: "webapp-1",
              allowedOperations: [],
              url: "https://new.example.com",
              source: {
                __typename: "IframeSource",
                url: "https://new.example.com",
              },
            },
          },
        },
      },
    };

    render(
      <TestApp mocks={[supersetInstancesMock, updateMock]}>
        <WebappForm workspace={workspace} webapp={webapp} />
      </TestApp>,
    );

    fireEvent.click(screen.getByText("Edit"));

    const urlInput = await screen.findByDisplayValue("https://old.example.com");
    fireEvent.change(urlInput, {
      target: { value: "https://new.example.com" },
    });

    fireEvent.click(screen.getByText("Save"));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "Web app updated successfully",
      );
    });

    const sentInput = updateVariables.mock.calls[0][0].input;
    expect(sentInput.source).toEqual({
      iframe: { url: "https://new.example.com" },
    });
    expect(sentInput).not.toHaveProperty("subdomain", null);
  });
});
