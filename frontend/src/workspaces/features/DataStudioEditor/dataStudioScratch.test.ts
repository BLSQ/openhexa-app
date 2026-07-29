import { clearUserData } from "core/helpers/userStorage";
import { clearScratch, readScratch, writeScratch } from "./dataStudioScratch";

const ws1 = { userId: "user-1", workspaceSlug: "ws-1" };
const ws2 = { userId: "user-1", workspaceSlug: "ws-2" };
const otherUser = { userId: "user-2", workspaceSlug: "ws-1" };

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
});
