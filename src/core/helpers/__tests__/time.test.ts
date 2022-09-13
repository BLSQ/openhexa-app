import { formatDuration } from "../time";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { i18n } from "next-i18next";

jest.mock("next-i18next", () => ({
  __esModule: true,
  i18n: {
    t: jest.fn(),
  },
}));

const tSpy = i18n!.t as jest.Mock;

describe("formatDuration", () => {
  afterEach(() => {
    tSpy.mockClear();
  });
  it("handles seconds", () => {
    formatDuration(0);
    expect(tSpy).toHaveBeenCalledWith("{{value}}s", { value: 0 });
    formatDuration(30);
    expect(tSpy).toHaveBeenCalledWith("{{value}}s", { value: 30 });
  });

  it("handles 90s", () => {
    formatDuration(90);
    expect(tSpy.mock.calls).toEqual([
      ["{{value}}m", { value: 1 }],
      ["{{value}}s", { value: 30 }],
    ]);
  });
  it("handles 3m50s", () => {
    formatDuration(3 * 60 + 50);
    expect(tSpy.mock.calls).toEqual([
      ["{{value}}m", { value: 3 }],
      ["{{value}}s", { value: 50 }],
    ]);
  });
  it("handles 42m 33s", () => {
    formatDuration(42 * 60 + 33);
    expect(tSpy.mock.calls).toEqual([
      ["{{value}}m", { value: 42 }],
      ["{{value}}s", { value: 33 }],
    ]);
  });
  it("handles the fuzziness for one hour", () => {
    formatDuration(60 * 60 + 0.9 * 60);
    expect(tSpy.mock.calls).toEqual([
      ["{{value}}m", { value: 60 }],
      ["{{value}}s", { value: 54 }],
    ]);
    tSpy.mockClear();

    formatDuration(60 * 60 + 0.9 * 60, 0.5);
    expect(tSpy.mock.calls).toEqual([
      ["{{value}}h", { value: 1 }],
      ["{{value}}s", { value: 54 }],
    ]);
  });

  it("handles days", () => {
    formatDuration(24 * 60 * 60 * 4 + 3 * 60 * 60 + 32 * 60 + 2);
    expect(tSpy.mock.calls).toEqual([
      ["{{value}}d", { value: 4 }],
      ["{{value}}h", { value: 3 }],
      ["{{value}}m", { value: 32 }],
      ["{{value}}s", { value: 2 }],
    ]);
  });
});
