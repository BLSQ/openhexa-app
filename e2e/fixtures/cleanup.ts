import { test as base } from "@playwright/test";

export type Cleanup = {
  /**
   * Registers how to undo something the test just created. Tasks run in reverse
   * order once the test ends, pass or fail, so a run that dies halfway through
   * still leaves the workspace as it found it.
   */
  add(label: string, undo: () => Promise<void>): void;
};

export const test = base.extend<{ cleanup: Cleanup }>({
  cleanup: async ({}, use) => {
    const tasks: { label: string; undo: () => Promise<void> }[] = [];

    await use({ add: (label, undo) => tasks.unshift({ label, undo }) });

    const failures: string[] = [];
    for (const { label, undo } of tasks) {
      try {
        await undo();
      } catch (error) {
        failures.push(`  - ${label}: ${(error as Error).message}`);
      }
    }
    if (failures.length > 0) {
      throw new Error(
        `Could not clean up after this test. Remove these by hand:\n${failures.join("\n")}`,
      );
    }
  },
});

export { expect } from "@playwright/test";
