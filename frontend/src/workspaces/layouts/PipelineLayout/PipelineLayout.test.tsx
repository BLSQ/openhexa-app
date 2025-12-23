import React from "react";
import { render } from "@testing-library/react";
import { PipelineType } from "graphql/types";
import PipelineLayout from "./index";
import { TestApp } from "core/helpers/testutils";

describe("PipelineLayout", () => {
  const pipeline = {
    permissions: {
      run: true,
      update: true,
      schedule: true,
      delete: true,
      createTemplateVersion: { isAllowed: true, reasons: [] },
    },
    webhookEnabled: false,
    id: "031be3e0-faac-48ab-bfc2-621a8076b240",
    createdAt: "2024-12-17T09:46:09.735Z",
    code: "simple-etl",
    name: "Simple ETL",
    description: "",
    type: PipelineType.ZipFile,
    currentVersion: {
      id: "5a1b38c3-d292-4c28-a8dd-a78034709101",
      versionName: "v1",
      config: {},
      parameters: [],
      isLatestVersion: true,
      createdAt: "2024-12-17T09:46:09.856Z",
      pipeline: {
        id: "031be3e0-faac-48ab-bfc2-621a8076b240",
        workspace: {
          slug: "test",
        },
        code: "simple-etl",
      },
      user: {
        displayName: "root@openhexa.org",
      },
    },
    recipients: [],
    workspace: {
      slug: "test",
    },
  };

  const workspace = {
    slug: "test",
    name: "Test",
    shortcuts: [],
    permissions: {
      manageMembers: true,
      update: true,
      launchNotebookServer: true,
    },
    countries: [
      {
        flag: "http://localhost:8000/static/flags/be.gif",
        code: "BE",
      },
    ],
  };

  it("should show 'Publish as Template' button when createTemplateVersion is true", () => {
    const { getByRole } = render(
      <TestApp>
        <PipelineLayout pipeline={pipeline} workspace={workspace}>
          <div>Child Content</div>
        </PipelineLayout>
      </TestApp>,
    );

    expect(
      getByRole("button", { name: "Publish as Template" }),
    ).toBeInTheDocument();
  });
});
