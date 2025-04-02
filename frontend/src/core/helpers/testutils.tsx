import { MockedProvider, MockedResponse } from "@apollo/client/testing";
import { faker } from "@faker-js/faker";
import { ByRoleOptions, screen } from "@testing-library/react";
import { MeProvider } from "identity/hooks/useMe";
import { ReactNode } from "react";

type TestAppProps = {
  children: ReactNode;
  mocks?: MockedResponse[];
  me?: any;
};

jest.mock("next/router", () => require("next-router-mock"));
// This is needed for mocking 'next/link':
jest.mock("next/dist/client/router", () => require("next-router-mock"));

export function TestApp(props: TestAppProps) {
  const me = {
    features: [],
    user: LOGGED_IN_USER,
    permissions: {
      adminPanel: true,
    },
    ...(props.me ?? {}),
  };
  return (
    <MockedProvider addTypename={true} mocks={props.mocks ?? []}>
      <MeProvider me={me}>{props.children}</MeProvider>
    </MockedProvider>
  );
}

export const LOGGED_IN_USER = {
  id: faker.string.uuid(),
  firstName: faker.person.firstName,
  lastName: faker.person.lastName,
  avatar: {
    initials: "AE",
    color: "red",
  },
};

export async function waitForDialog(options?: ByRoleOptions) {
  const dialog = await screen.findByRole("dialog", options);
  return dialog;
}

export async function frames(count: number) {
  for (let n = 0; n <= count; n++) {
    await new Promise<void>((resolve) =>
      requestAnimationFrame(() => resolve()),
    );
  }
}

export function assertHidden(element: HTMLElement | null) {
  try {
    if (element === null) return expect(element).not.toBe(null);

    expect(element).toHaveAttribute("hidden");
    expect(element).toHaveStyle({ display: "none" });
  } catch (err) {
    if (err instanceof Error) Error.captureStackTrace(err, assertHidden);
    throw err;
  }
}

export function assertVisible(element: HTMLElement | null) {
  try {
    if (element === null) return expect(element).not.toBe(null);

    expect(element).not.toHaveAttribute("hidden");
    expect(element).not.toHaveStyle({ display: "none" });
  } catch (err) {
    if (err instanceof Error) Error.captureStackTrace(err, assertVisible);
    throw err;
  }
}
