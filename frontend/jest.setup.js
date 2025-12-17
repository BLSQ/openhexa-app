// Optional: configure or set up a testing framework before each test.
// If you delete this file, remove `setupFilesAfterEnv` from `jest.config.js`

// Learn more: https://github.com/testing-library/jest-dom
import "@testing-library/jest-dom";
import { faker } from "@faker-js/faker";

import {
  configMocks,
  mockAnimationsApi,
  mockResizeObserver,
} from "jsdom-testing-mocks";
import { act } from "react";
import { Settings } from "luxon";

// Set environment variables for tests
process.env.OPENHEXA_BACKEND_URL = "http://localhost:8000";
process.env.NEXT_PUBLIC_OPENHEXA_BACKEND_URL = "http://localhost:8000";
process.env.NEXT_PUBLIC_SENTRY_DSN = "";
process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT = "test";
process.env.NEXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE = "1";
process.env.NEXT_PUBLIC_DISABLE_ANALYTICS = "true";
process.env.SENTRY_DSN = "";
process.env.SENTRY_TRACES_SAMPLE_RATE = "1";

Settings.defaultLocale = "en";
Settings.defaultZone = "Europe/Brussels";
Settings.now = jest.fn().mockImplementation(() => Date.now());

// To not have to wrap everything in act()
globalThis.IS_REACT_ACT_ENVIRONMENT = true;
configMocks({ act });

globalThis.resizeObserverMock = mockResizeObserver();

mockAnimationsApi();

beforeEach(() => {
  // Set seed for faker
  faker.seed(1);
});
afterEach(() => {
  window.localStorage.clear();
});

// Mock browser confirm
window.confirm = jest.fn();

jest.mock("react", () => {
  const actualReact = jest.requireActual("react");
  return {
    ...actualReact,
    useId() {
      const ref = actualReact.useRef(faker.string.uuid());
      return ref.current;
    },
  };
});

jest.mock("core/components/MarkdownEditor/MarkdownEditor");
jest.mock("core/helpers", () => ({
  stripMarkdown: (markdown) => markdown,
}));
jest.mock("next-i18next", () => ({
  I18nextProvider: jest.fn(),
  useTranslation: () => ({ t: (key) => key }),
  __esModule: true,
}));

jest.mock("next/router", () => require("next-router-mock"));
// This is needed for mocking 'next/link':
jest.mock("next/dist/client/router", () => require("next-router-mock"));

// https://github.com/scottrippey/next-router-mock/issues/58#issuecomment-1182861712
// Fixes the navigation using links
jest.mock("next/dist/shared/lib/router-context.shared-runtime", () => {
  const { createContext } = require("react");
  const router = require("next-router-mock").default;
  const RouterContext = createContext(router);
  return { RouterContext };
});

jest.mock("@mdxeditor/editor", () => ({
  __esModule: true,
  default: jest.fn(),
}));

jest.mock("remark-gfm", () => ({
  __esModule: true,
  default: jest.fn(),
}));
