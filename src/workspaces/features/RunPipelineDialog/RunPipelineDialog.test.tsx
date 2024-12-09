import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { v4 } from "uuid";

import { useLazyQuery } from "@apollo/client";
import { UserEvent } from "@testing-library/user-event/dist/types/setup/setup";
import { runPipeline } from "workspaces/helpers/pipelines";
import RunPipelineDialog from "../RunPipelineDialog";
import { ParameterField_ParameterFragment } from "./ParameterField.generated";
import { PipelineType } from "graphql/types";

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
  parameters: Array<ParameterField_ParameterFragment>,
) => {
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
      name: "3",
      createdAt: "2023-06-21T13:27:59.928Z",
      user: {
        displayName: "test",
      },
      parameters,
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
        type: "bool",
        default: null,
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
        type: "bool",
        default: null,
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
        type: "int",
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
        type: "int",
        default: null,
        required: true,
        choices: null,
        multiple: false,
      },

      {
        code: "float_param",
        name: "float_param",
        type: "float",
        default: 2.1,
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
        type: "str",
        default: null,
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
        type: "str",
        default: null,
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
        type: "int",
        default: null,
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
});
