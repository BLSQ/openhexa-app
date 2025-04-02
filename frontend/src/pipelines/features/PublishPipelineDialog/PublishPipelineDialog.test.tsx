import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import PublishPipelineDialog from "./PublishPipelineDialog";
import { MockedProvider } from "@apollo/client/testing";
import { toast } from "react-toastify";
import i18n from "i18next";
import { I18nextProvider, initReactI18next } from "react-i18next";
import messages from "../../../../public/locales/en/messages.json";

i18n.use(initReactI18next).init({
  lng: "en",
  fallbackLng: "en",
  ns: ["messages"],
  defaultNS: "messages",
  debug: true,
  resources: { en: { messages } },
});

jest.mock("react-toastify", () => ({
  toast: {
    success: jest.fn(),
  },
}));

const createPipelineTemplateVersionMock = jest.fn();
jest.mock("pipelines/graphql/mutations.generated", () => ({
  useCreatePipelineTemplateVersionMutation: () => [
    createPipelineTemplateVersionMock,
  ],
}));

const pipeline = {
  id: "pipeline-id",
  currentVersion: { id: "version-id", versionName: "version-name" },
  template: null,
};

const workspace = {
  slug: "workspace-slug",
};

const renderPublishPipelineDialog = (pipelineOverride = {}) => {
  createPipelineTemplateVersionMock.mockResolvedValue({
    data: {
      createPipelineTemplateVersion: {
        success: true,
        errors: [],
      },
    },
  });

  render(
    <MockedProvider>
      <I18nextProvider i18n={i18n}>
        <PublishPipelineDialog
          open={true}
          onClose={jest.fn()}
          pipeline={{ ...pipeline, ...pipelineOverride }}
          workspace={workspace}
        />
      </I18nextProvider>
    </MockedProvider>,
  );
};

describe("PublishPipelineDialog", () => {
  it("submits the form successfully for a new template", async () => {
    renderPublishPipelineDialog();

    fireEvent.change(screen.getByLabelText("Template name"), {
      target: { value: "Test Template" },
    });
    fireEvent.change(screen.getByLabelText("Template description"), {
      target: { value: "Test Description" },
    });

    const submitButton = screen.getByRole("button", {
      name: "Create a new Template",
    });
    expect(submitButton).toBeDisabled();

    fireEvent.click(screen.getByLabelText("Confirm publishing"));
    expect(submitButton).not.toBeDisabled();

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(createPipelineTemplateVersionMock).toHaveBeenCalledWith({
        variables: {
          input: {
            name: "Test Template",
            code: "Test Template",
            description: "Test Description",
            config: undefined,
            changelog: "",
            workspaceSlug: "workspace-slug",
            pipelineId: "pipeline-id",
            pipelineVersionId: "version-id",
          },
        },
      });
    });

    expect(toast.success).toHaveBeenCalledWith(
      "New Template 'Test Template' created successfully.",
    );
  });

  it("submits the form successfully for an existing template", async () => {
    renderPublishPipelineDialog({
      template: { name: "template-name" },
    });

    const submitButton = screen.getByRole("button", {
      name: "Add a new version to Template 'template-name'",
    });
    expect(submitButton).toBeDisabled();

    fireEvent.click(screen.getByLabelText("Confirm publishing"));
    expect(submitButton).not.toBeDisabled();

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(createPipelineTemplateVersionMock).toHaveBeenCalledWith({
        variables: {
          input: {
            name: "",
            code: "",
            description: "",
            config: undefined,
            changelog: "",
            workspaceSlug: "workspace-slug",
            pipelineId: "pipeline-id",
            pipelineVersionId: "version-id",
          },
        },
      });
    });

    expect(toast.success).toHaveBeenCalledWith(
      "New Template Version for 'template-name' created successfully.",
    );
  });
});
