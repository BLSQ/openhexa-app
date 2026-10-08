import { fireEvent, render, screen } from "@testing-library/react";
import AssistantProposalBanner from "./index";

jest.mock("next-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

describe("AssistantProposalBanner", () => {
  it("shows the message as read-only text when it cannot be edited", () => {
    render(
      <AssistantProposalBanner
        label="Proposed version"
        message="Add retry logic"
        onDismiss={jest.fn()}
      />,
    );

    expect(screen.getByText("Add retry logic")).toBeInTheDocument();
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
  });

  it("renders the message in an editable input and reports changes", () => {
    const onMessageChange = jest.fn();
    render(
      <AssistantProposalBanner
        label="Proposed version"
        message="Add retry logic"
        onMessageChange={onMessageChange}
        onDismiss={jest.fn()}
      />,
    );

    const input = screen.getByRole("textbox");
    expect(input).toHaveValue("Add retry logic");

    fireEvent.change(input, { target: { value: "Add retry logic and a cap" } });
    expect(onMessageChange).toHaveBeenCalledWith("Add retry logic and a cap");
  });

  it("renders an empty input when the agent proposed no message", () => {
    render(
      <AssistantProposalBanner
        label="Proposed version"
        onMessageChange={jest.fn()}
        onDismiss={jest.fn()}
      />,
    );

    expect(screen.getByRole("textbox")).toHaveValue("");
  });
});
