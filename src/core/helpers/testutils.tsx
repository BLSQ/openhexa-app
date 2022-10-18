import { MockedProvider, MockedResponse } from "@apollo/client/testing";
import { faker } from "@faker-js/faker";
import { ByRoleOptions, screen } from "@testing-library/react";
import { ReactNode } from "react";

type TestAppProps = {
  children: ReactNode;
  mocks?: MockedResponse[];
};

jest.mock("next/router", () => require("next-router-mock"));
// This is needed for mocking 'next/link':
jest.mock("next/dist/client/router", () => require("next-router-mock"));
jest.mock("identity/hooks/useMe");

export function TestApp(props: TestAppProps) {
  return (
    <MockedProvider addTypename={false} mocks={props.mocks ?? []}>
      {props.children}
    </MockedProvider>
  );
}

export const LOGGED_IN_USER = {
  id: faker.datatype.uuid(),
  firstName: faker.name.firstName,
  lastName: faker.name.lastName,
  avatar: {
    initials: "AE",
    color: "red",
  },
};

export async function waitForDialog(options?: ByRoleOptions) {
  const dialog = await screen.getByRole("dialog", options);
  return dialog;
}
