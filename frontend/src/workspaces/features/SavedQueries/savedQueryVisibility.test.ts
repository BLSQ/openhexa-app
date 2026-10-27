import { SavedQueryVisibility } from "graphql/types";
import { canChangeVisibility } from "./savedQueryVisibility";

const { Private, Workspace, Public } = SavedQueryVisibility;

describe("canChangeVisibility", () => {
  const author = { canShare: true, canPublish: true };
  const admin = { canShare: false, canPublish: true };
  const editor = { canShare: false, canPublish: false };

  it("lets the author make any switch", () => {
    expect(canChangeVisibility(Private, Public, author)).toBe(true);
    expect(canChangeVisibility(Public, Private, author)).toBe(true);
  });

  it("lets an admin publish and take a query back to the workspace", () => {
    expect(canChangeVisibility(Workspace, Public, admin)).toBe(true);
    expect(canChangeVisibility(Public, Workspace, admin)).toBe(true);
  });

  // Anyone but the author would hand the query to its author and lose it.
  it("keeps going private the author's call", () => {
    expect(canChangeVisibility(Public, Private, admin)).toBe(false);
    expect(canChangeVisibility(Workspace, Private, admin)).toBe(false);
  });

  it("refuses every switch to someone with neither right", () => {
    expect(canChangeVisibility(Workspace, Public, editor)).toBe(false);
    expect(canChangeVisibility(Workspace, Private, editor)).toBe(false);
  });

  it("always allows keeping the current visibility", () => {
    expect(canChangeVisibility(Public, Public, editor)).toBe(true);
  });
});
