import { render } from "@testing-library/react";
import { deleteConnection } from "workspaces/helpers/connections/utils";
import DeleteConnectionTrigger from "./DeleteConnectionTrigger";

jest.mock("workspaces/helpers/connections/utils", () => ({
  __esModule: true,
  ...jest.requireActual("workspaces/helpers/connections/utils"),
  deleteConnection: jest.fn(),
}));

describe("DeleteConnectionTrigger", () => {
  it("renders the child if the user can delete the connection", async () => {
    const CONNECTION = {
      id: "1",
      name: "",
      permissions: {
        delete: true,
      },
    };
    const Children = jest.fn().mockReturnValue(null);
    const { container } = render(
      <DeleteConnectionTrigger workspace={{ id: "1" }} connection={CONNECTION}>
        {Children}
      </DeleteConnectionTrigger>,
    );

    expect(Children).toHaveBeenCalled();
  });

  it("does not render if user does not have the permission", async () => {
    const CONNECTION = {
      id: "",
      name: "",
      permissions: {
        delete: false,
      },
    };
    const Children = jest.fn().mockReturnValue(null);
    const { container } = render(
      <DeleteConnectionTrigger workspace={{ id: "" }} connection={CONNECTION}>
        {Children}
      </DeleteConnectionTrigger>,
    );

    expect(Children).not.toHaveBeenCalled();
  });

  it("deletes the connection on confirm", async () => {
    const CONNECTION = {
      id: "C_ID",
      name: "",
      permissions: {
        delete: true,
      },
    };
    const Children = jest.fn().mockReturnValue(null);
    const { container } = render(
      <DeleteConnectionTrigger
        workspace={{ id: "W_ID" }}
        connection={CONNECTION}
      >
        {Children}
      </DeleteConnectionTrigger>,
    );

    expect(Children).toHaveBeenCalled();
    expect(window.confirm).not.toHaveBeenCalled();

    const { onClick } = Children.mock.calls[0][0];
    (window.confirm as jest.Mock).mockReturnValue(false);
    onClick();
    expect(window.confirm).toHaveBeenCalled();
    expect(deleteConnection).not.toHaveBeenCalled();

    (window.confirm as jest.Mock).mockReturnValue(true);
    onClick();
    expect(window.confirm).toHaveBeenCalled();
    expect(deleteConnection).toHaveBeenCalledWith("C_ID");
  });
});
