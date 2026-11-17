import { DatasetVisibility } from "graphql/types";
import {
  canChangeDatasetVisibility,
  getPublicSlugError,
  normalizePublicSlug,
} from "./datasetSharing";

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

describe("normalizePublicSlug", () => {
  it("lowercases, strips accents and turns spaces and dots into hyphens", () => {
    expect(normalizePublicSlug("Données Été.v2")).toBe("donnees-ete-v2");
  });

  it("leaves other characters for validation to report", () => {
    expect(normalizePublicSlug("a/b")).toBe("a/b");
  });
});

describe("getPublicSlugError", () => {
  it.each(["my-dataset", "malaria_2024-v2", "health", "dhis2"])(
    "accepts %s",
    (slug) => expect(getPublicSlugError(slug)).toBeNull(),
  );

  it.each(["", "-my", "my_", "my--ds", "my-_ds", "a/b", "a".repeat(256)])(
    "rejects the format of %s",
    (slug) => expect(getPublicSlugError(slug)).toBe("INVALID_FORMAT"),
  );

  it("rejects reserved route names", () => {
    expect(getPublicSlugError("new")).toBe("RESERVED");
  });
});
