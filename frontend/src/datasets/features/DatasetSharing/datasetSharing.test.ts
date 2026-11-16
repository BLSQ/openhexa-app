import { DatasetVisibility } from "graphql/types";
import { canChangeDatasetVisibility } from "./datasetSharing";

const { Workspace, Organization, Public } = DatasetVisibility;

describe("canChangeDatasetVisibility", () => {
  const sharer = { canUpdate: true, canShare: true };
  const editor = { canUpdate: true, canShare: false };
  const viewer = { canUpdate: false, canShare: false };

  it("lets a sharer make and take back a public dataset", () => {
    expect(canChangeDatasetVisibility(Workspace, Public, sharer)).toBe(true);
    expect(canChangeDatasetVisibility(Public, Organization, sharer)).toBe(true);
  });

  it("lets an editor switch between workspace and organization only", () => {
    expect(canChangeDatasetVisibility(Workspace, Organization, editor)).toBe(
      true,
    );
    expect(canChangeDatasetVisibility(Organization, Public, editor)).toBe(
      false,
    );
    expect(canChangeDatasetVisibility(Public, Workspace, editor)).toBe(false);
  });

  it("refuses every switch to a viewer, but keeps the current value", () => {
    expect(canChangeDatasetVisibility(Workspace, Organization, viewer)).toBe(
      false,
    );
    expect(canChangeDatasetVisibility(Public, Public, viewer)).toBe(true);
  });
});
