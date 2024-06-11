import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import GeneratePipelineWebhookUrlDialog from ".";
import { faker } from "@faker-js/faker";
import {
  GenerateNewDatabasePasswordDocument,
  useGenerateWebhookPipelineWebhookUrlMutation,
} from "workspaces/graphql/mutations.generated";

jest.mock("workspaces/graphql/mutations.generated", () => ({
  ...jest.requireActual("workspaces/graphql/mutations.generated"),
  __esModule: true,
  useGenerateWebhookPipelineWebhookUrlMutation: jest.fn().mockReturnValue([]),
}));

const PIPELINE = {
  id: faker.string.uuid(),
  code: faker.string.alphanumeric(),
};

const useGenerateWebhookPipelineWebhookUrlMutationMock =
  useGenerateWebhookPipelineWebhookUrlMutation as jest.Mock;

describe("GeneratePipelineWebhookUrlDialog", () => {
  const onClose = jest.fn();
  beforeEach(() => {
    useGenerateWebhookPipelineWebhookUrlMutationMock.mockClear();
  });

  it("is displayed when open is true", async () => {
    const { container } = render(
      <TestApp mocks={[]}>
        <GeneratePipelineWebhookUrlDialog
          pipeline={PIPELINE}
          open={true}
          onClose={() => {}}
        />
      </TestApp>,
    );

    const dialog = await screen.queryByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(container).toMatchSnapshot();
  });

  it("Generates new webhook url", async () => {
    const { useGenerateNewDatabasePasswordMutation } = jest.requireActual(
      "workspaces/graphql/mutations.generated",
    );
    useGenerateWebhookPipelineWebhookUrlMutationMock.mockImplementation(
      useGenerateNewDatabasePasswordMutation,
    );

    const user = userEvent.setup();
    const mocks = [
      {
        request: {
          query: GenerateNewDatabasePasswordDocument,
          variables: {
            input: {
              id: PIPELINE.id,
            },
          },
        },
        result: {
          data: {
            generatePipelineWebhookUrl: {
              success: true,
              errors: [],
              pipeline: {
                webhookUrl:
                  "http://app.openhexa.test/pipelines/random_string/run",
              },
            },
          },
        },
      },
    ];

    const { container } = render(
      <TestApp mocks={mocks}>
        <GeneratePipelineWebhookUrlDialog
          pipeline={PIPELINE}
          open={true}
          onClose={() => {}}
        />
      </TestApp>,
    );

    const saveButton = screen.getByRole("button", { name: "Generate new url" });
    await user.click(saveButton);

    expect(useGenerateWebhookPipelineWebhookUrlMutationMock).toHaveBeenCalled();
  });
});
