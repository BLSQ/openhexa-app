import { render } from "@testing-library/react";
import DeleteDatabaseTableTrigger from "./DeleteDatabaseTableTrigger";
import { deleteTable } from "workspaces/helpers/database";

jest.mock("workspaces/helpers/database", () => ({
  __esModule: true,
  ...jest.requireActual("workspaces/helpers/database"),
  deleteTable: jest.fn(),
}));

describe("DeleteDatabaseTableTrigger", () => {
  it("renders the child if the user can delete the connection", async () => {
    const WORKSPACE = {
      slug: "slug",
      permissions: {
        deleteDatabaseTable: true,
      },
    };
    const Children = jest.fn().mockReturnValue(null);
    const { container } = render(
      <DeleteDatabaseTableTrigger
        workspace={WORKSPACE}
        table={{ name: "random" }}
      >
        {Children}
      </DeleteDatabaseTableTrigger>,
    );

    expect(Children).toHaveBeenCalled();
  });

  it("does not render if user does not have the permission", async () => {
    const WORKSPACE = {
      slug: "slug",
      permissions: {
        deleteDatabaseTable: false,
      },
    };
    const Children = jest.fn().mockReturnValue(null);
    const { container } = render(
      <DeleteDatabaseTableTrigger
        workspace={WORKSPACE}
        table={{ name: "random" }}
      >
        {Children}
      </DeleteDatabaseTableTrigger>,
    );

    expect(Children).not.toHaveBeenCalled();
  });

  it("deletes the table on confirm", async () => {
    const WORKSPACE = {
      slug: "slug",
      permissions: {
        deleteDatabaseTable: true,
      },
    };
    const Children = jest.fn().mockReturnValue(null);
    const { container } = render(
      <DeleteDatabaseTableTrigger
        workspace={WORKSPACE}
        table={{ name: "random" }}
      >
        {Children}
      </DeleteDatabaseTableTrigger>,
    );

    expect(Children).toHaveBeenCalled();
    expect(window.confirm).not.toHaveBeenCalled();

    const { onClick } = Children.mock.calls[0][0];
    (window.confirm as jest.Mock).mockReturnValue(false);
    onClick();
    expect(window.confirm).toHaveBeenCalled();
    expect(deleteTable).not.toHaveBeenCalled();

    (window.confirm as jest.Mock).mockReturnValue(true);
    onClick();
    expect(window.confirm).toHaveBeenCalled();
    expect(deleteTable).toHaveBeenCalledWith("slug", "random");
  });
});
