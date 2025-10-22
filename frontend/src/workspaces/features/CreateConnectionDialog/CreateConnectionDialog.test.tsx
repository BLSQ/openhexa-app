import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import CreateConnectionDialog from "./CreateConnectionDialog";
import { useMutation } from "@apollo/client/react";
import { graphql } from "graphql/gql";

const CreateConnectionDoc = graphql(`
mutation createConnection($input: CreateConnectionInput!) {
  createConnection(input: $input) {
    success
    connection {
      id
      name
    }
    errors
  }
}
`);

jest.mock("workspaces/graphql/mutations.generated", () => ({
  __esModule: true,
  ...jest.requireActual("workspaces/graphql/mutations.generated"),
  useCreateConnectionMutation: jest.fn().mockReturnValue([]),
}));

describe("CreateConnectionDialog", () => {
  const onClose = jest.fn();
  const WORKSPACE = {
    slug: "ID",
  };

  afterEach(() => {
    onClose.mockReset();
  });

  it("renders", async () => {
    render(
      <TestApp>
        <CreateConnectionDialog open onClose={onClose} workspace={WORKSPACE} />
      </TestApp>,
    );

    const customConnectionElement = await screen.findByText("Custom");
    expect(customConnectionElement).toBeInTheDocument();
  });

  it("creates a custom connection", async () => {
    const createConnectionMock = jest.fn();
    (useMutation as jest.Mock).mockReturnValue(CreateConnectionDoc, [
      createConnectionMock,
    ]);
    const user = userEvent.setup();
    render(
      <TestApp>
        <CreateConnectionDialog open onClose={onClose} workspace={WORKSPACE} />
      </TestApp>,
    );

    const customConnectionElement = await screen.findByText("Custom");
    expect(customConnectionElement).toBeInTheDocument();

    await user.click(customConnectionElement);
    await user.type(
      screen.getByRole("textbox", { name: "Connection name" }),
      "My Connection",
    );
    await user.type(
      screen.getByRole("textbox", { name: "Description" }),
      "Description",
    );

    await user.click(screen.getByTestId("add-field"));
    await user.type(
      screen.getByRole("textbox", { name: "Field name" }),
      "field",
    );
    await user.type(
      screen.getByRole("textbox", { name: "Field value" }),
      "val",
    );
    expect(createConnectionMock).not.toHaveBeenCalled();
    await user.click(screen.getByTestId("create-connection"));
    expect(createConnectionMock).toHaveBeenCalledWith({
      variables: {
        input: {
          workspaceSlug: WORKSPACE.slug,
          name: "My Connection",
          description: "Description",
          type: "CUSTOM",
          fields: [
            {
              code: "field",
              value: "val",
              secret: false,
            },
          ],
        },
      },
    });
  });
});
