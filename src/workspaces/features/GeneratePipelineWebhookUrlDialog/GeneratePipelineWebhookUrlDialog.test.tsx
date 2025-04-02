import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import GeneratePipelineWebhookUrlDialog from ".";
import { faker } from "@faker-js/faker";

const mutationMock = jest.fn();

jest.mock("@apollo/client", () => ({
  ...jest.requireActual("@apollo/client"),
  useMutation: jest.fn().mockImplementation(() => [mutationMock]),
}));

const PIPELINE = {
  id: faker.string.uuid(),
  code: faker.string.alphanumeric(),
};

describe("GeneratePipelineWebhookUrlDialog", () => {
  const onClose = jest.fn();
  beforeEach(() => {
    mutationMock.mockClear();
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
    mutationMock.mockReturnValue({
      data: { generatePipelineWebhookUrl: { errors: [], success: true } },
    });

    const user = userEvent.setup();

    const { container } = render(
      <GeneratePipelineWebhookUrlDialog
        pipeline={PIPELINE}
        open={true}
        onClose={() => {}}
      />,
    );

    const saveButton = screen.getByRole("button", { name: "Generate" });
    await user.click(saveButton);

    expect(mutationMock).toHaveBeenCalled();
  });
});
