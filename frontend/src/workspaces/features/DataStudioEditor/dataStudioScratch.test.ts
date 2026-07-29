import { clearScratch, readScratch, writeScratch } from "./dataStudioScratch";

describe("dataStudioScratch", () => {
  it("keeps a draft per workspace", () => {
    writeScratch("ws-1", "SELECT 1");
    writeScratch("ws-2", "SELECT 2");

    expect(readScratch("ws-1")).toBe("SELECT 1");
    expect(readScratch("ws-2")).toBe("SELECT 2");
  });

  it("returns an empty draft for a workspace that has none", () => {
    expect(readScratch("ws-1")).toBe("");
  });

  it("drops the draft when the editor is emptied", () => {
    writeScratch("ws-1", "SELECT 1");
    writeScratch("ws-1", "");

    expect(readScratch("ws-1")).toBe("");
  });

  it("drops the draft rather than storing an oversized one", () => {
    writeScratch("ws-1", "SELECT 1");
    writeScratch("ws-1", "x".repeat(100_001));

    expect(readScratch("ws-1")).toBe("");
  });

  it("clears the draft", () => {
    writeScratch("ws-1", "SELECT 1");
    clearScratch("ws-1");

    expect(readScratch("ws-1")).toBe("");
  });

  it("tolerates unavailable storage", () => {
    jest.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("Storage is full");
    });
    jest.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("Storage is unavailable");
    });

    expect(() => writeScratch("ws-1", "SELECT 1")).not.toThrow();
    expect(readScratch("ws-1")).toBe("");
  });
});
