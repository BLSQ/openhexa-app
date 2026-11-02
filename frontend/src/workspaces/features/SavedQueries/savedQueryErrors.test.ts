import type { TFunction } from "i18next";
import { CreateSavedQueryError, UpdateSavedQueryError } from "graphql/types";
import {
  createSavedQueryErrorMessage,
  updateSavedQueryErrorMessage,
} from "./savedQueryErrors";

const t = ((key: string) => key) as unknown as TFunction;

describe("savedQueryErrors", () => {
  it("names every create error code", () => {
    for (const code of Object.values(CreateSavedQueryError)) {
      expect(createSavedQueryErrorMessage([code], t)).not.toBe("Unknown error");
    }
  });

  it("names every update error code", () => {
    for (const code of Object.values(UpdateSavedQueryError)) {
      expect(updateSavedQueryErrorMessage([code], t)).not.toBe("Unknown error");
    }
  });

  it("tells a template error apart from a declaration error", () => {
    expect(
      createSavedQueryErrorMessage([CreateSavedQueryError.InvalidTemplate], t),
    ).toContain("not declared");
    expect(
      updateSavedQueryErrorMessage(
        [UpdateSavedQueryError.InvalidParameters],
        t,
      ),
    ).toContain("declarations");
  });
});
