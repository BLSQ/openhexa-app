const nextJest = require("next/jest");

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files in your test environment
  dir: "./",
});

// Add any custom config to be passed to Jest
const customJestConfig = {
  setupFilesAfterEnv: ["<rootDir>/jest.setup.js"],
  modulePaths: ["<rootDir>/src/"],
  testEnvironment: "jest-environment-jsdom",
  reporters: ["default", process.env.CI ? "github-actions" : null].filter(
    Boolean,
  ),
  clearMocks: true,
  restoreMocks: true,
};

// See : https://github.com/vercel/next.js/issues/35634#issuecomment-1115250297
async function jestConfig() {
  const nextJestConfig = await createJestConfig(customJestConfig)();
  // /node_modules/ is the first pattern
  nextJestConfig.transformIgnorePatterns[0] =
    "/node_modules/(?!react-hotkeys-hook)/";
  return nextJestConfig;
}

module.exports = jestConfig;
