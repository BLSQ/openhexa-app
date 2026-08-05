import { hasSavePath } from "./savePath";

describe("hasSavePath", () => {
  const saved = { isSaved: true, hasContent: true };
  const unsaved = { isSaved: false, hasContent: true };

  it("lets an editor update the query in place", () => {
    expect(hasSavePath({ ...saved, canUpdate: true, canCreate: false })).toBe(
      true,
    );
  });

  it("lets a viewer fork the query into a new one", () => {
    expect(hasSavePath({ ...saved, canUpdate: false, canCreate: true })).toBe(
      true,
    );
  });

  it("has nowhere to put a viewer's changes when they cannot fork either", () => {
    expect(hasSavePath({ ...saved, canUpdate: false, canCreate: false })).toBe(
      false,
    );
  });

  it("needs create rights for a query that was never saved", () => {
    expect(hasSavePath({ ...unsaved, canUpdate: true, canCreate: false })).toBe(
      false,
    );
    expect(hasSavePath({ ...unsaved, canUpdate: false, canCreate: true })).toBe(
      true,
    );
  });

  it("has nothing to save once the buffer is empty", () => {
    expect(
      hasSavePath({
        isSaved: true,
        hasContent: false,
        canUpdate: true,
        canCreate: true,
      }),
    ).toBe(false);
  });
});
