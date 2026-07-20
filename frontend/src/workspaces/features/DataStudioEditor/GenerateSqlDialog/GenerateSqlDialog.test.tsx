import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import GenerateSqlDialog from "./GenerateSqlDialog";
import {
  GenerateSqlFormInstance,
  GenerateSqlPhase,
} from "./useGenerateSqlForm";

const makeForm = (
  overrides: Partial<GenerateSqlFormInstance> = {},
): GenerateSqlFormInstance => ({
  prompt: "",
  setPrompt: jest.fn(),
  handleSubmit: jest.fn(),
  cancel: jest.fn(),
  phase: GenerateSqlPhase.Idle,
  error: null,
  reset: jest.fn(),
  ...overrides,
});

describe("GenerateSqlDialog", () => {
  it("resets the form when it opens", () => {
    const form = makeForm();
    render(
      <GenerateSqlDialog
        open
        onClose={jest.fn()}
        form={form}
        monthlyLimitExceeded={false}
      />,
    );
    expect(form.reset).toHaveBeenCalled();
  });

  it("disables Generate until a prompt is entered", () => {
    const form = makeForm();
    render(
      <GenerateSqlDialog
        open
        onClose={jest.fn()}
        form={form}
        monthlyLimitExceeded={false}
      />,
    );
    expect(screen.getByRole("button", { name: "Generate" })).toBeDisabled();
  });

  it("submits the prompt when Generate is clicked", async () => {
    const form = makeForm({ prompt: "top 10 patients" });
    render(
      <GenerateSqlDialog
        open
        onClose={jest.fn()}
        form={form}
        monthlyLimitExceeded={false}
      />,
    );
    await userEvent.click(screen.getByRole("button", { name: "Generate" }));
    expect(form.handleSubmit).toHaveBeenCalled();
  });

  it("shows a generating state and disables the textarea while streaming", () => {
    const form = makeForm({
      prompt: "top 10 patients",
      phase: GenerateSqlPhase.Generating,
    });
    render(
      <GenerateSqlDialog
        open
        onClose={jest.fn()}
        form={form}
        monthlyLimitExceeded={false}
      />,
    );
    expect(screen.getByText("Generating SQL query")).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/most recent records/i)).toBeDisabled();
    expect(screen.getByRole("button", { name: "Generate" })).toBeDisabled();
  });

  it("shows a success checkmark once the query is generated", () => {
    const form = makeForm({
      prompt: "top 10 patients",
      phase: GenerateSqlPhase.Done,
    });
    render(
      <GenerateSqlDialog
        open
        onClose={jest.fn()}
        form={form}
        monthlyLimitExceeded={false}
      />,
    );
    expect(screen.getByText("Generating SQL query")).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Cancel" }),
    ).not.toBeInTheDocument();
  });

  it("shows the error message with a retry action", async () => {
    const form = makeForm({
      prompt: "top 10 patients",
      phase: GenerateSqlPhase.Error,
      error: "Something went wrong.",
    });
    render(
      <GenerateSqlDialog
        open
        onClose={jest.fn()}
        form={form}
        monthlyLimitExceeded={false}
      />,
    );
    expect(screen.getByText("Something went wrong.")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(form.handleSubmit).toHaveBeenCalled();
  });

  it("cancels an in-flight generation via the inline Cancel link", async () => {
    const form = makeForm({ phase: GenerateSqlPhase.Generating });
    render(
      <GenerateSqlDialog
        open
        onClose={jest.fn()}
        form={form}
        monthlyLimitExceeded={false}
      />,
    );

    await userEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(form.cancel).toHaveBeenCalled();
  });

  it("cancels an in-flight generation when closed via the footer Close button", async () => {
    const form = makeForm({ phase: GenerateSqlPhase.Generating });
    const onClose = jest.fn();
    render(
      <GenerateSqlDialog
        open
        onClose={onClose}
        form={form}
        monthlyLimitExceeded={false}
      />,
    );

    await userEvent.click(screen.getByRole("button", { name: "Close" }));

    expect(form.cancel).toHaveBeenCalled();
    expect(onClose).toHaveBeenCalled();
  });

  it("replaces the form with a limit-reached banner and hides Generate", () => {
    const form = makeForm();
    render(
      <GenerateSqlDialog
        open
        onClose={jest.fn()}
        form={form}
        monthlyLimitExceeded
      />,
    );
    expect(
      screen.getByText(/reached your monthly usage limit/i),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Generate" }),
    ).not.toBeInTheDocument();
  });
});
