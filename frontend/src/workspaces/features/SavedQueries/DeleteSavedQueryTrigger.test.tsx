import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { toast } from "react-toastify";
import DeleteSavedQueryTrigger from "./DeleteSavedQueryTrigger";

const deleteMock = jest.fn();

jest.mock("workspaces/features/SavedQueries/SavedQueries.generated", () => ({
  useDeleteSavedQueryMutation: () => [deleteMock],
}));

jest.mock("react-toastify", () => ({
  toast: { success: jest.fn(), error: jest.fn() },
}));

jest.mock("core/hooks/useCacheKey", () => ({
  __esModule: true,
  default: () => jest.fn(),
}));

const savedQuery = {
  id: "q1",
  name: "Query One",
  permissions: { update: true, delete: true },
} as any;

const renderTrigger = (sq: any = savedQuery, onDelete = jest.fn()) =>
  render(
    <DeleteSavedQueryTrigger savedQuery={sq} onDelete={onDelete}>
      {({ onClick }) => <button onClick={onClick}>delete</button>}
    </DeleteSavedQueryTrigger>,
  );

beforeEach(() => jest.clearAllMocks());

describe("DeleteSavedQueryTrigger", () => {
  it("renders nothing without delete permission", () => {
    renderTrigger({ ...savedQuery, permissions: { delete: false } });
    expect(screen.queryByText("delete")).not.toBeInTheDocument();
  });

  it("does not delete when the confirm is dismissed", () => {
    (window.confirm as jest.Mock).mockReturnValue(false);
    renderTrigger();

    fireEvent.click(screen.getByText("delete"));

    expect(window.confirm).toHaveBeenCalled();
    expect(deleteMock).not.toHaveBeenCalled();
  });

  it("deletes on confirm and reports success", async () => {
    (window.confirm as jest.Mock).mockReturnValue(true);
    deleteMock.mockResolvedValue({
      data: { deleteSavedQuery: { success: true, errors: [] } },
    });
    const onDelete = jest.fn();
    renderTrigger(savedQuery, onDelete);

    fireEvent.click(screen.getByText("delete"));

    await waitFor(() =>
      expect(deleteMock).toHaveBeenCalledWith({
        variables: { input: { id: "q1" } },
      }),
    );
    expect(onDelete).toHaveBeenCalled();
    expect(toast.success).toHaveBeenCalledWith("Saved query deleted");
  });

  it("reports an error when the backend rejects the delete", async () => {
    (window.confirm as jest.Mock).mockReturnValue(true);
    deleteMock.mockResolvedValue({
      data: {
        deleteSavedQuery: { success: false, errors: ["PERMISSION_DENIED"] },
      },
    });
    renderTrigger();

    fireEvent.click(screen.getByText("delete"));

    await waitFor(() => expect(toast.error).toHaveBeenCalled());
  });
});
