import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import GenerateSqlBar from "./GenerateSqlBar";
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

describe("GenerateSqlBar", () => {
  it("renders nothing when closed", () => {
    const form = makeForm();
    render(
      <GenerateSqlBar
        open={false}
        onClose={jest.fn()}
        form={form}
        monthlyLimitExceeded={false}
      />,
    );
    expect(
      screen.queryByPlaceholderText(/describe what you'd like to query/i),
    ).not.toBeInTheDocument();
  });

  it("resets the form when it opens", () => {
    const form = makeForm();
    render(
      <GenerateSqlBar
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
      <GenerateSqlBar
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
      <GenerateSqlBar
        open
        onClose={jest.fn()}
        form={form}
        monthlyLimitExceeded={false}
      />,
    );
    await userEvent.click(screen.getByRole("button", { name: "Generate" }));
    expect(form.handleSubmit).toHaveBeenCalled();
  });

  it("shows a generating state and disables the input while streaming", () => {
    const form = makeForm({
      prompt: "top 10 patients",
      phase: GenerateSqlPhase.Generating,
    });
    render(
      <GenerateSqlBar
        open
        onClose={jest.fn()}
        form={form}
        monthlyLimitExceeded={false}
      />,
    );
    expect(
      screen.getByPlaceholderText(/describe what you'd like to query/i),
    ).toBeDisabled();
    expect(
      screen.getByRole("button", { name: "Generating…" }),
    ).toBeDisabled();
  });

  it("shows the error message with a retry action", async () => {
    const form = makeForm({
      prompt: "top 10 patients",
      phase: GenerateSqlPhase.Error,
      error: "Something went wrong.",
    });
    render(
      <GenerateSqlBar
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

  it("cancels an in-flight generation and closes when Cancel is clicked", async () => {
    const form = makeForm({ phase: GenerateSqlPhase.Generating });
    const onClose = jest.fn();
    render(
      <GenerateSqlBar
        open
        onClose={onClose}
        form={form}
        monthlyLimitExceeded={false}
      />,
    );

    await userEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(form.cancel).toHaveBeenCalled();
    expect(onClose).toHaveBeenCalled();
  });

  it("closes without cancelling when idle", async () => {
    const form = makeForm();
    const onClose = jest.fn();
    render(
      <GenerateSqlBar
        open
        onClose={onClose}
        form={form}
        monthlyLimitExceeded={false}
      />,
    );

    await userEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(form.cancel).not.toHaveBeenCalled();
    expect(onClose).toHaveBeenCalled();
  });

  it("closes on Escape", async () => {
    const form = makeForm();
    const onClose = jest.fn();
    render(
      <GenerateSqlBar
        open
        onClose={onClose}
        form={form}
        monthlyLimitExceeded={false}
      />,
    );

    await userEvent.type(
      screen.getByPlaceholderText(/describe what you'd like to query/i),
      "{Escape}",
    );

    expect(onClose).toHaveBeenCalled();
  });

  it("replaces the bar with a limit-reached banner and hides Generate", () => {
    const form = makeForm();
    render(
      <GenerateSqlBar
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
