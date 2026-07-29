import { clearUserData } from "core/helpers/userStorage";
import {
  clearScratch,
  readScratch,
  sweepScratch,
  writeScratch,
} from "./dataStudioScratch";

const ws1 = { userId: "user-1", workspaceSlug: "ws-1" };
const ws2 = { userId: "user-1", workspaceSlug: "ws-2" };
const otherUser = { userId: "user-2", workspaceSlug: "ws-1" };

const KEY_PREFIX = "user-data.data-studio.scratch.";
const keyOf = ({ userId, workspaceSlug }: typeof ws1) =>
  `${KEY_PREFIX}${userId}.${workspaceSlug}`;

const DAY_MS = 24 * 60 * 60 * 1000;
const START = new Date("2026-07-01T00:00:00Z").getTime();

const scratchKeys = () =>
  Object.keys(window.localStorage).filter((key) => key.startsWith(KEY_PREFIX));

beforeEach(() => {
  jest.useFakeTimers();
  jest.setSystemTime(START);
});

afterEach(() => {
  jest.useRealTimers();
});

describe("dataStudioScratch", () => {
  it("keeps a draft per workspace", () => {
    writeScratch(ws1, "SELECT 1");
    writeScratch(ws2, "SELECT 2");

    expect(readScratch(ws1)).toBe("SELECT 1");
    expect(readScratch(ws2)).toBe("SELECT 2");
  });

  it("keeps a draft per user, so a shared browser does not leak one", () => {
    writeScratch(ws1, "SELECT secret FROM patients");

    expect(readScratch(otherUser)).toBe("");
  });

  it("returns an empty draft for a workspace that has none", () => {
    expect(readScratch(ws1)).toBe("");
  });

  it("drops the draft when the editor is emptied", () => {
    writeScratch(ws1, "SELECT 1");
    writeScratch(ws1, "");

    expect(readScratch(ws1)).toBe("");
  });

  it("drops the draft rather than storing an oversized one", () => {
    writeScratch(ws1, "SELECT 1");
    writeScratch(ws1, "x".repeat(100_001));

    expect(readScratch(ws1)).toBe("");
  });

  it("clears the draft", () => {
    writeScratch(ws1, "SELECT 1");
    clearScratch(ws1);

    expect(readScratch(ws1)).toBe("");
  });

  it("is stored where logging out clears it", () => {
    writeScratch(ws1, "SELECT 1");

    clearUserData();

    expect(readScratch(ws1)).toBe("");
  });

  it("tolerates unavailable storage", () => {
    jest.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("Storage is full");
    });
    jest.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("Storage is unavailable");
    });

    expect(() => writeScratch(ws1, "SELECT 1")).not.toThrow();
    expect(readScratch(ws1)).toBe("");
  });

  describe("retention", () => {
    it("still returns a draft within the retention window", () => {
      writeScratch(ws1, "SELECT 1");

      jest.setSystemTime(START + 29 * DAY_MS);

      expect(readScratch(ws1)).toBe("SELECT 1");
    });

    it("forgets a draft once it is older than the retention window", () => {
      writeScratch(ws1, "SELECT 1");

      jest.setSystemTime(START + 31 * DAY_MS);

      expect(readScratch(ws1)).toBe("");
    });

    it("refreshes the retention window on each edit", () => {
      writeScratch(ws1, "SELECT 1");

      jest.setSystemTime(START + 29 * DAY_MS);
      writeScratch(ws1, "SELECT 2");
      jest.setSystemTime(START + 50 * DAY_MS);

      expect(readScratch(ws1)).toBe("SELECT 2");
    });

    it("ignores a value left by an unrecognised storage format", () => {
      window.localStorage.setItem(keyOf(ws1), "SELECT 1");

      expect(readScratch(ws1)).toBe("");
    });
  });

  describe("sweeping", () => {
    it("collects expired drafts, including ones never reopened", () => {
      writeScratch(ws1, "SELECT 1");
      writeScratch(ws2, "SELECT 2");

      jest.setSystemTime(START + 31 * DAY_MS);
      sweepScratch();

      expect(scratchKeys()).toEqual([]);
    });

    it("keeps drafts that are still within the window", () => {
      writeScratch(ws1, "SELECT 1");

      jest.setSystemTime(START + 29 * DAY_MS);
      sweepScratch();

      expect(readScratch(ws1)).toBe("SELECT 1");
    });

    it("collects entries it cannot read", () => {
      window.localStorage.setItem(keyOf(ws1), "not json");
      window.localStorage.setItem(keyOf(ws2), JSON.stringify({ content: "x" }));

      sweepScratch();

      expect(scratchKeys()).toEqual([]);
    });

    it("caps how many drafts accumulate, dropping the least recent", () => {
      for (let n = 0; n < 25; n++) {
        jest.setSystemTime(START + n * 1000);
        writeScratch({ userId: "user-1", workspaceSlug: `ws-${n}` }, `Q${n}`);
      }

      sweepScratch();

      expect(scratchKeys()).toHaveLength(20);
      // The five oldest went; the newest stayed.
      expect(readScratch({ userId: "user-1", workspaceSlug: "ws-4" })).toBe("");
      expect(readScratch({ userId: "user-1", workspaceSlug: "ws-5" })).toBe(
        "Q5",
      );
      expect(readScratch({ userId: "user-1", workspaceSlug: "ws-24" })).toBe(
        "Q24",
      );
    });

    it("leaves other namespaces alone", () => {
      window.localStorage.setItem("last-visited-workspace", "ws-1");
      window.localStorage.setItem("user-data.other-feature.x", "keep me");

      jest.setSystemTime(START + 31 * DAY_MS);
      sweepScratch();

      expect(window.localStorage.getItem("last-visited-workspace")).toBe("ws-1");
      expect(window.localStorage.getItem("user-data.other-feature.x")).toBe(
        "keep me",
      );
    });

    it("tolerates unavailable storage", () => {
      jest.spyOn(Storage.prototype, "removeItem").mockImplementation(() => {
        throw new Error("Storage is unavailable");
      });
      window.localStorage.setItem(keyOf(ws1), "not json");

      expect(() => sweepScratch()).not.toThrow();
    });
  });
});
