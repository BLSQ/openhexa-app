import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { v4 } from "uuid";

import { useLazyQuery } from "@apollo/client";
import { UserEvent } from "@testing-library/user-event/dist/types/setup/setup";
import { runPipeline } from "workspaces/helpers/pipelines";
import RunPipelineDialog from "../RunPipelineDialog";
import { RunPipelineDialog_PipelineFragment } from "./RunPipelineDialog.generated";
import { ParameterType, PipelineType } from "graphql/types";
import { makeParameter } from "./parameterFixtures";

type TestPipeline = RunPipelineDialog_PipelineFragment & {
  currentVersion: NonNullable<
    RunPipelineDialog_PipelineFragment["currentVersion"]
  >;
};

jest.mock("@apollo/client", () => ({
  ...jest.requireActual("@apollo/client"),
  __esModule: true,
  useLazyQuery: jest.fn(),
}));

jest.mock("workspaces/helpers/pipelines", () => ({
  ...jest.requireActual("workspaces/helpers/pipelines"),
  __esModule: true,
  runPipeline: jest.fn(),
}));

const useLazyQueryMock = useLazyQuery as jest.Mock;

const pipelineWithParameters = (
  parameters: Array<Parameters<typeof makeParameter>[0]>,
): TestPipeline => {
  return {
    id: v4(),
    code: "code",
    type: PipelineType.ZipFile,
    workspace: {
      slug: "slug",
    },
    permissions: {
      run: true,
    },
    currentVersion: {
      id: v4(),
      versionName: "3",
      createdAt: "2023-06-21T13:27:59.928Z",
      user: {
        displayName: "test",
      },
      parameters: parameters.map(makeParameter),
    },
  };
};

const runPipelineMock = runPipeline as jest.Mock;

describe("RunPipelineDialog", () => {
  const submitForm = async (user: UserEvent) => {
    const submitBtn = await screen.getByRole("button", { name: "Run" });
    await user.click(submitBtn);
  };
  it("calls the runPipeline with a optional bool", async () => {
    const pipeline = pipelineWithParameters([
      {
        code: "is_ok",
        name: "is_ok",
        type: ParameterType.Bool,
        default: null,
        widget: null,
        connection: null,
        required: false,
        choices: null,
        multiple: false,
      },
    ]);
    const mockFetch = jest
      .fn()
      .mockResolvedValue({ data: { pipelineByCode: pipeline } });
    useLazyQueryMock.mockReturnValue([
      mockFetch,
      { loading: false, data: { pipelineByCode: pipeline } },
    ]);

    const user = userEvent.setup();
    render(
      <RunPipelineDialog pipeline={pipeline}>
        {(onClick) => (
          <button data-testid="trigger" onClick={onClick}>
            Trigger
          </button>
        )}
      </RunPipelineDialog>,
    );
    await user.click(await screen.findByTestId("trigger"));
    await submitForm(user);
    expect(runPipelineMock).toHaveBeenCalledWith(
      pipeline.id,
      { is_ok: undefined },
      pipeline.currentVersion.id,
      true,
      false,
    );
  });

  it("configures the run to receive the result by mail", async () => {
    const pipeline = pipelineWithParameters([]);
    const mockFetch = jest
      .fn()
      .mockResolvedValue({ data: { pipelineByCode: pipeline } });
    useLazyQueryMock.mockReturnValue([
      mockFetch,
      { loading: false, data: { pipelineByCode: pipeline } },
    ]);

    const user = userEvent.setup();

    render(
      <RunPipelineDialog pipeline={pipeline}>
        {(onClick) => (
          <button data-testid="trigger" onClick={onClick}>
            Trigger
          </button>
        )}
      </RunPipelineDialog>,
    );
    await user.click(await screen.findByTestId("trigger"));
    await user.click(await screen.findByText("Advanced settings"));
    await user.click(await screen.findByLabelText("Send notifications"));
    await user.click(await screen.findByLabelText("Show debug messages"));
    await submitForm(user);
    expect(runPipelineMock).toHaveBeenCalledWith(
      pipeline.id,
      {},
      pipeline.currentVersion.id,
      false,
      true,
    );
  });

  it("calls the runPipeline with a required bool not checked", async () => {
    const pipeline = pipelineWithParameters([
      {
        code: "is_ok",
        name: "is_ok",
        type: ParameterType.Bool,
        default: null,
        widget: null,
        connection: null,
        required: true,
        choices: null,
        multiple: false,
      },
    ]);
    const mockFetch = jest
      .fn()
      .mockResolvedValue({ data: { pipelineByCode: pipeline } });
    useLazyQueryMock.mockReturnValue([
      mockFetch,
      { loading: false, data: { pipelineByCode: pipeline } },
    ]);

    const user = userEvent.setup();

    render(
      <RunPipelineDialog pipeline={pipeline}>
        {(onClick) => (
          <button data-testid="trigger" onClick={onClick}>
            Trigger
          </button>
        )}
      </RunPipelineDialog>,
    );
    await user.click(await screen.findByTestId("trigger"));

    await submitForm(user);
    expect(runPipelineMock).toHaveBeenCalled();
  });

  it("calls the runPipeline with a optional int", async () => {
    const pipeline = pipelineWithParameters([
      {
        code: "int",
        name: "int",
        type: ParameterType.Int,
        required: false,
        choices: null,
        widget: null,
        connection: null,
        multiple: false,
      },
    ]);
    const mockFetch = jest
      .fn()
      .mockResolvedValue({ data: { pipelineByCode: pipeline } });
    useLazyQueryMock.mockReturnValue([
      mockFetch,
      { loading: false, data: { pipelineByCode: pipeline } },
    ]);

    const user = userEvent.setup();
    render(
      <RunPipelineDialog pipeline={pipeline}>
        {(onClick) => (
          <button data-testid="trigger" onClick={onClick}>
            Trigger
          </button>
        )}
      </RunPipelineDialog>,
    );
    await user.click(await screen.findByTestId("trigger"));

    await submitForm(user);
    expect(runPipelineMock).toHaveBeenCalledWith(
      pipeline.id,
      {},
      pipeline.currentVersion.id,
      true,
      false,
    );
  });

  it("handles required int & float parameter", async () => {
    const pipeline = pipelineWithParameters([
      {
        code: "int_param",
        name: "int_param",
        type: ParameterType.Int,
        default: null,
        required: true,
        choices: null,
        widget: null,
        connection: null,
        multiple: false,
      },

      {
        code: "float_param",
        name: "float_param",
        type: ParameterType.Float,
        default: 2.1,
        required: false,
        choices: null,
        widget: null,
        connection: null,
        multiple: false,
      },
    ]);
    const mockFetch = jest
      .fn()
      .mockResolvedValue({ data: { pipelineByCode: pipeline } });
    useLazyQueryMock.mockReturnValue([
      mockFetch,
      { loading: false, data: { pipelineByCode: pipeline } },
    ]);
    const user = userEvent.setup();

    render(
      <RunPipelineDialog pipeline={pipeline}>
        {(onClick) => (
          <button data-testid="trigger" onClick={onClick}>
            Trigger
          </button>
        )}
      </RunPipelineDialog>,
    );
    await user.click(await screen.findByTestId("trigger"));

    await submitForm(user);
    expect(runPipelineMock).not.toHaveBeenCalled();

    // Fill in the form
    await user.type(await screen.findByLabelText("int_param"), "0");
    await user.clear(await screen.findByLabelText("float_param"));
    await user.type(await screen.findByLabelText("float_param"), "2.2ABBCDER");

    await submitForm(user);
    expect(runPipelineMock).toHaveBeenCalledWith(
      pipeline.id,
      { int_param: 0, float_param: 2.2 },
      pipeline.currentVersion.id,
      true,
      false,
    );
  });

  it("handles multiline parameter", async () => {
    const pipeline = pipelineWithParameters([
      {
        code: "multi",
        name: "multi",
        type: ParameterType.Str,
        default: null,
        widget: null,
        connection: null,
        required: true,
        choices: null,
        multiple: true,
      },
    ]);
    const mockFetch = jest
      .fn()
      .mockResolvedValue({ data: { pipelineByCode: pipeline } });
    useLazyQueryMock.mockReturnValue([
      mockFetch,
      { loading: false, data: { pipelineByCode: pipeline } },
    ]);

    const user = userEvent.setup();

    render(
      <RunPipelineDialog pipeline={pipeline}>
        {(onClick) => (
          <button data-testid="trigger" onClick={onClick}>
            Trigger
          </button>
        )}
      </RunPipelineDialog>,
    );
    await user.click(await screen.findByTestId("trigger"));

    await submitForm(user);
    expect(runPipelineMock).not.toHaveBeenCalled();

    // Fill in the form
    await user.type(await screen.findByLabelText("multi"), "0\n1\n2");

    await submitForm(user);
    expect(runPipelineMock).toHaveBeenCalledWith(
      pipeline.id,
      { multi: ["0", "1", "2"] },
      pipeline.currentVersion.id,
      true,
      false,
    );
  });

  it("handles required str parameter", async () => {
    const pipeline = pipelineWithParameters([
      {
        code: "string",
        name: "string",
        type: ParameterType.Str,
        default: null,
        widget: null,
        connection: null,
        required: true,
        choices: null,
        multiple: false,
      },
    ]);
    const mockFetch = jest
      .fn()
      .mockResolvedValue({ data: { pipelineByCode: pipeline } });
    useLazyQueryMock.mockReturnValue([
      mockFetch,
      { loading: false, data: { pipelineByCode: pipeline } },
    ]);

    const user = userEvent.setup();

    render(
      <RunPipelineDialog pipeline={pipeline}>
        {(onClick) => (
          <button data-testid="trigger" onClick={onClick}>
            Trigger
          </button>
        )}
      </RunPipelineDialog>,
    );
    await user.click(await screen.findByTestId("trigger"));

    await submitForm(user);
    expect(runPipelineMock).not.toHaveBeenCalled();

    // Fill in the form
    await user.type(await screen.findByLabelText("string"), "coucou");

    await submitForm(user);
    expect(runPipelineMock).toHaveBeenCalledWith(
      pipeline.id,
      { string: "coucou" },
      pipeline.currentVersion.id,
      true,
      false,
    );
  });

  it("handles choices parameter", async () => {
    const pipeline = pipelineWithParameters([
      {
        code: "choices_param",
        name: "choices_param",
        type: ParameterType.Int,
        default: null,
        widget: null,
        connection: null,
        required: true,
        choices: [1, 2, 3],
        multiple: false,
      },
    ]);
    const mockFetch = jest
      .fn()
      .mockResolvedValue({ data: { pipelineByCode: pipeline } });
    useLazyQueryMock.mockReturnValue([
      mockFetch,
      { loading: false, data: { pipelineByCode: pipeline } },
    ]);

    const user = userEvent.setup();

    render(
      <RunPipelineDialog pipeline={pipeline}>
        {(onClick) => (
          <button data-testid="trigger" onClick={onClick}>
            Trigger
          </button>
        )}
      </RunPipelineDialog>,
    );
    await user.click(await screen.findByTestId("trigger"));

    await submitForm(user);
    expect(runPipelineMock).not.toHaveBeenCalled();

    // Fill in the form
    const comboboxButtons = await screen.findAllByTestId("combobox-button");
    await user.click(comboboxButtons[0]);
    await user.click(await screen.findByText("2"));

    await submitForm(user);
    expect(runPipelineMock).toHaveBeenCalledWith(
      pipeline.id,
      { choices_param: 2 },
      pipeline.currentVersion.id,
      true,
      false,
    );
  });

  const pipelineWithDisablingToggle = () =>
    pipelineWithParameters([
      {
        code: "run_report_only",
        name: "Run report only",
        type: ParameterType.Bool,
        default: false,
        widget: null,
        connection: null,
        required: false,
        choices: null,
        multiple: false,
        disables: ["data_input"],
        disableWhen: true,
      },
      {
        code: "data_input",
        name: "data_input",
        type: ParameterType.Str,
        default: null,
        widget: null,
        connection: null,
        required: true,
        choices: null,
        multiple: false,
        disables: [],
        disableWhen: true,
      },
    ]);

  it("skips required validation for a parameter disabled by a toggle", async () => {
    const pipeline = pipelineWithDisablingToggle();
    const mockFetch = jest
      .fn()
      .mockResolvedValue({ data: { pipelineByCode: pipeline } });
    useLazyQueryMock.mockReturnValue([
      mockFetch,
      { loading: false, data: { pipelineByCode: pipeline } },
    ]);

    const user = userEvent.setup();
    render(
      <RunPipelineDialog pipeline={pipeline}>
        {(onClick) => (
          <button data-testid="trigger" onClick={onClick}>
            Trigger
          </button>
        )}
      </RunPipelineDialog>,
    );
    await user.click(await screen.findByTestId("trigger"));

    // data_input is required and empty: submitting must be blocked.
    await submitForm(user);
    expect(runPipelineMock).not.toHaveBeenCalled();

    // Turning the toggle on disables data_input and exempts it from validation.
    await user.click(await screen.findByRole("switch"));
    await submitForm(user);
    expect(runPipelineMock).toHaveBeenCalledWith(
      pipeline.id,
      { run_report_only: true },
      pipeline.currentVersion.id,
      true,
      false,
    );
  });

  it("re-enables validation for a parameter when its toggle is turned back off", async () => {
    const pipeline = pipelineWithDisablingToggle();
    const mockFetch = jest
      .fn()
      .mockResolvedValue({ data: { pipelineByCode: pipeline } });
    useLazyQueryMock.mockReturnValue([
      mockFetch,
      { loading: false, data: { pipelineByCode: pipeline } },
    ]);

    const user = userEvent.setup();
    render(
      <RunPipelineDialog pipeline={pipeline}>
        {(onClick) => (
          <button data-testid="trigger" onClick={onClick}>
            Trigger
          </button>
        )}
      </RunPipelineDialog>,
    );
    await user.click(await screen.findByTestId("trigger"));

    // Toggle on then off again: data_input is required once more.
    const toggle = await screen.findByRole("switch");
    await user.click(toggle);
    await user.click(toggle);
    await submitForm(user);
    expect(runPipelineMock).not.toHaveBeenCalled();

    // Filling it in unblocks the run, and the toggle value is sent.
    await user.type(await screen.findByLabelText("data_input"), "real");
    await submitForm(user);
    expect(runPipelineMock).toHaveBeenCalledWith(
      pipeline.id,
      { run_report_only: false, data_input: "real" },
      pipeline.currentVersion.id,
      true,
      false,
    );
  });

  it("shows which toggle disabled a parameter", async () => {
    const pipeline = pipelineWithDisablingToggle();
    const mockFetch = jest
      .fn()
      .mockResolvedValue({ data: { pipelineByCode: pipeline } });
    useLazyQueryMock.mockReturnValue([
      mockFetch,
      { loading: false, data: { pipelineByCode: pipeline } },
    ]);

    const user = userEvent.setup();
    render(
      <RunPipelineDialog pipeline={pipeline}>
        {(onClick) => (
          <button data-testid="trigger" onClick={onClick}>
            Trigger
          </button>
        )}
      </RunPipelineDialog>,
    );
    await user.click(await screen.findByTestId("trigger"));

    // The i18n mock returns the key verbatim, so we assert on the prefix
    // rather than the interpolated controller name.
    expect(screen.queryByText(/Disabled by/)).not.toBeInTheDocument();
    await user.click(await screen.findByRole("switch"));
    expect(await screen.findByText(/Disabled by/)).toBeInTheDocument();
  });
});
