import { renderHook } from "@testing-library/react";
import usePipelineRunPoller, { randomInterval } from "./usePipelineRunPoller";
import { util } from "prettier";
import { useLazyQuery } from "@apollo/client";
import { PipelineRunStatus } from "graphql-types";

const useLazyQueryMock = useLazyQuery as jest.Mock;

jest.mock("@apollo/client", () => ({
  ...jest.requireActual("@apollo/client"),
  __esModule: true,
  useLazyQuery: jest.fn(),
}));

describe("randomInterval", () => {
  it("works", () => {
    jest.spyOn(Math, "random").mockReturnValue(0.3);
    expect(randomInterval(1000, 0.1)).toBe(1000 * (1 - 0.3 * 0.1));

    jest.spyOn(Math, "random").mockReturnValue(0.6);
    expect(randomInterval(1000, 0.1)).toBe(1000 * (1 + 0.6 * 0.1));
  });
});

describe("usePipelineRunPoller", () => {
  const startPollingMock = jest.fn();
  const stopPollingMock = jest.fn();

  beforeEach(() => {
    startPollingMock.mockReset();
    stopPollingMock.mockReset();
  });

  it("does not tries to poll when no run id is given", async () => {
    useLazyQueryMock.mockReturnValue([
      null,
      {
        data: null,
        startPolling: startPollingMock,
        stopPolling: stopPollingMock,
      },
    ]);
    const { result } = renderHook(() => usePipelineRunPoller(null));

    expect(startPollingMock).not.toHaveBeenCalled();
    expect(stopPollingMock).toHaveBeenCalled();
  });

  it("tries to poll when run id is given", async () => {
    useLazyQueryMock.mockReturnValue([
      null,
      {
        data: null,
        startPolling: startPollingMock,
        stopPolling: stopPollingMock,
      },
    ]);

    renderHook(() => usePipelineRunPoller("MY_ID"));

    expect(startPollingMock).toHaveBeenCalled();
    expect(stopPollingMock).not.toHaveBeenCalled();
    expect(useLazyQueryMock).toHaveBeenCalledWith(expect.anything(), {
      variables: { runId: "MY_ID" },
    });
  });

  it("stops polling when run is finished", async () => {
    useLazyQueryMock.mockReturnValue([
      null,
      {
        data: { status: PipelineRunStatus.Success },
        startPolling: startPollingMock,
        stopPolling: stopPollingMock,
      },
    ]);

    renderHook(() => usePipelineRunPoller("MY_ID"));

    expect(startPollingMock).not.toHaveBeenCalled();
    expect(stopPollingMock).toHaveBeenCalled();
  });
});
