import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import { useCreateSelfHostedOrganizationMutation } from "organizations/graphql/mutations.generated";
import CreateOrganizationDialog from "./CreateOrganizationDialog";

jest.mock("organizations/graphql/mutations.generated", () => ({
  ...jest.requireActual("organizations/graphql/mutations.generated"),
  __esModule: true,
  useCreateSelfHostedOrganizationMutation: jest.fn().mockReturnValue([]),
}));

const useCreateSelfHostedOrganizationMutationMock =
  useCreateSelfHostedOrganizationMutation as jest.Mock;

describe("CreateOrganizationDialog", () => {
  beforeEach(() => {
    useCreateSelfHostedOrganizationMutationMock.mockClear();
  });

  it("is not displayed when open is false", async () => {
    render(<CreateOrganizationDialog open={false} onClose={() => {}} />);
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("is displayed when open is true", async () => {
    render(
      <TestApp mocks={[]}>
        <CreateOrganizationDialog open onClose={() => {}} />
      </TestApp>,
    );
    expect(screen.queryByRole("dialog")).toBeInTheDocument();
  });

  it("creates an organization with the entered name", async () => {
    const mutate = jest.fn().mockResolvedValue({
      data: {
        createSelfHostedOrganization: {
          success: true,
          errors: [],
          organization: { id: "org-1", name: "Test Org" },
        },
      },
    });
    useCreateSelfHostedOrganizationMutationMock.mockReturnValue([mutate]);
    const user = userEvent.setup();

    render(
      <TestApp>
        <CreateOrganizationDialog open onClose={() => {}} />
      </TestApp>,
    );

    const createButton = screen.getByRole("button", { name: "Create" });
    await user.click(createButton);
    expect(mutate).not.toHaveBeenCalled();

    await user.type(screen.getByTestId("name"), "Test Org");
    await user.click(createButton);

    expect(mutate).toHaveBeenCalledWith({
      variables: {
        input: {
          name: "Test Org",
          shortName: undefined,
        },
      },
    });
  });
});
