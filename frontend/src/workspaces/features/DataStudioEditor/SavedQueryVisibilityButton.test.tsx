import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { SavedQueryVisibility } from "graphql/types";
import SavedQueryVisibilityButton from "./SavedQueryVisibilityButton";

const renderButton = (props: any = {}) => {
  const onChange = props.onChange ?? jest.fn();
  render(
    <SavedQueryVisibilityButton
      visibility={props.visibility ?? SavedQueryVisibility.Private}
      canUpdate={props.canUpdate ?? true}
      saving={props.saving ?? false}
      onChange={onChange}
    />,
  );
  return onChange;
};

const openMenu = () =>
  fireEvent.click(screen.getByRole("button", { name: /Private|Workspace/ }));

beforeEach(() => jest.clearAllMocks());

describe("SavedQueryVisibilityButton", () => {
  it("shows the current visibility", () => {
    renderButton({ visibility: SavedQueryVisibility.Workspace });
    expect(
      screen.getByRole("button", { name: /Workspace/ }),
    ).toBeInTheDocument();
  });

  it("shares the query straight away", async () => {
    const onChange = renderButton({
      visibility: SavedQueryVisibility.Private,
    });

    openMenu();
    fireEvent.click(await screen.findByRole("menuitem", { name: /Workspace/ }));

    await waitFor(() =>
      expect(onChange).toHaveBeenCalledWith(SavedQueryVisibility.Workspace),
    );
  });

  // Unsharing takes the query away from colleagues, so it is not a one-click action.
  it("asks to confirm before making a shared query private", async () => {
    const onChange = renderButton({
      visibility: SavedQueryVisibility.Workspace,
    });

    openMenu();
    fireEvent.click(await screen.findByRole("menuitem", { name: /Private/ }));

    expect(
      await screen.findByText("Make this query private?"),
    ).toBeInTheDocument();
    expect(onChange).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: "Make private" }));

    await waitFor(() =>
      expect(onChange).toHaveBeenCalledWith(SavedQueryVisibility.Private),
    );
  });

  it("leaves the query shared when the confirmation is cancelled", async () => {
    const onChange = renderButton({
      visibility: SavedQueryVisibility.Workspace,
    });

    openMenu();
    fireEvent.click(await screen.findByRole("menuitem", { name: /Private/ }));
    fireEvent.click(await screen.findByRole("button", { name: "Cancel" }));

    await waitFor(() =>
      expect(screen.queryByText("Make this query private?")).toBeNull(),
    );
    expect(onChange).not.toHaveBeenCalled();
  });

  it("does not mutate when the current visibility is re-selected", async () => {
    const onChange = renderButton({
      visibility: SavedQueryVisibility.Workspace,
    });

    openMenu();
    fireEvent.click(await screen.findByRole("menuitem", { name: /Workspace/ }));

    expect(onChange).not.toHaveBeenCalled();
  });

  it("renders a read-only badge without the permission to unshare", () => {
    renderButton({
      visibility: SavedQueryVisibility.Workspace,
      canUpdate: false,
    });

    expect(screen.getByText("Workspace")).toBeInTheDocument();
    expect(screen.queryByRole("button")).toBeNull();
  });
});
