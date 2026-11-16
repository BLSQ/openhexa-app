import playwright from "eslint-plugin-playwright";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["node_modules/", "playwright-report/", "test-results/"] },
  {
    files: ["**/*.ts"],
    extends: [tseslint.configs.base, playwright.configs["flat/recommended"]],
    languageOptions: {
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    rules: {
      // A Playwright call left without `await` passes while checking nothing.
      "@typescript-eslint/no-floating-promises": "error",
      "@typescript-eslint/no-misused-promises": "error",
      "@typescript-eslint/await-thenable": "error",
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-unused-vars": "error",
      // Skips here depend on which optional accounts are configured.
      "playwright/no-skipped-test": ["error", { allowConditional: true }],
      // Page objects assert on behalf of the specs that call them.
      "playwright/expect-expect": "off",
      // Specs branch on the environment (is there a mailbox?) and on what the
      // app answered (which slug to clean up), which these two cannot tell
      // from a test that only sometimes checks.
      "playwright/no-conditional-in-test": "off",
      "playwright/no-conditional-expect": "off",
    },
  },
);
