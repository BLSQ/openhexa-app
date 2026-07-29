import { clearUserData, userDataKey } from "../userStorage";

describe("userDataKey", () => {
  it("namespaces the parts it is given", () => {
    expect(userDataKey("editor.draft", "user-1", "ws-1")).toBe(
      "user-data.editor.draft.user-1.ws-1",
    );
  });
});

describe("clearUserData", () => {
  it("removes every namespaced entry", () => {
    window.localStorage.setItem(userDataKey("a", "user-1"), "1");
    window.localStorage.setItem(userDataKey("b", "user-1"), "2");

    clearUserData();

    expect(window.localStorage.length).toBe(0);
  });

  it("leaves entries outside the namespace alone", () => {
    window.localStorage.setItem("last-visited-workspace", "ws-1");
    window.localStorage.setItem(userDataKey("a", "user-1"), "1");

    clearUserData();

    expect(window.localStorage.getItem("last-visited-workspace")).toBe("ws-1");
    expect(window.localStorage.getItem(userDataKey("a", "user-1"))).toBeNull();
  });

  it("tolerates unavailable storage", () => {
    jest.spyOn(Storage.prototype, "removeItem").mockImplementation(() => {
      throw new Error("Storage is unavailable");
    });
    window.localStorage.setItem(userDataKey("a", "user-1"), "1");

    expect(() => clearUserData()).not.toThrow();
  });
});
