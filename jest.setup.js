// Optional: configure or set up a testing framework before each test.
// If you delete this file, remove `setupFilesAfterEnv` from `jest.config.js`

// Used for __tests__/testing-library.js
// Learn more: https://github.com/testing-library/jest-dom
import "@testing-library/jest-dom/extend-expect";
import { faker } from "@faker-js/faker";
import { setConfig } from "next/config";
// @ts-ignore
import { publicRuntimeConfig } from "./next.config";

// Make sure you can use "publicRuntimeConfig" within tests.
setConfig({
  publicRuntimeConfig: {
    ...publicRuntimeConfig,
    GRAPHQL_ENDPOINT: "http://localhost:3000/graphql/",
  },
});

// Set seed for faker
faker.seed(1);

jest.mock("react-i18next", () => ({
  I18nextProvider: jest.fn(),
  useTranslation: () => ({ t: (key) => key }),
  __esmodule: true,
}));

jest.mock("next/router", () => require("next-router-mock"));
// This is needed for mocking 'next/link':
jest.mock("next/dist/client/router", () => require("next-router-mock"));

// https://github.com/scottrippey/next-router-mock/issues/58#issuecomment-1182861712
// Fixes the navigation using links
jest.mock("next/dist/shared/lib/router-context", () => {
  const { createContext } = require("react");
  const router = require("next-router-mock").default;
  const RouterContext = createContext(router);
  return { RouterContext };
});

// Mock the IntersectionObserver
const intersectionObserverMock = () => ({
  observe: () => null,
  unobserve: () => null,
  disconnect: () => null,
});
window.IntersectionObserver = jest
  .fn()
  .mockImplementation(intersectionObserverMock);

// Mock @headlessui/react to disable animations

jest.mock("@headlessui/react", () => ({
  __esModule: true,
  ...jest.requireActual("@headlessui/react"),
}));
