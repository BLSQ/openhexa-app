import PipelineRunFavoriteTrigger from "./PipelineRunFavoriteTrigger";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MockedProvider } from "@apollo/client/testing";
import { waitForDialog } from "core/helpers/testutils";

const mutationMock = jest.fn();

jest.mock("@apollo/client", () => ({
  ...jest.requireActual("@apollo/client"),
  useMutation: jest.fn().mockImplementation(() => [mutationMock]),
}));

const confirmSpy = jest.spyOn(window, "confirm").mockReturnValue(true);

describe("PipelineRunFavoriteTrigger", () => {
  afterEach(() => {
    mutationMock.mockClear();
    confirmSpy.mockClear();
  });

  it("renders the trigger and not the dialog", async () => {
    const { container, debug } = render(
      <MockedProvider>
        <PipelineRunFavoriteTrigger run={{ isFavorite: false, id: "1" }} />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });

  it("opens the dialog on click when not favorite", async () => {
    const user = userEvent.setup();

    mutationMock.mockReturnValue({ data: jest.fn() });
    const { container, debug } = render(
      <PipelineRunFavoriteTrigger run={{ isFavorite: false, id: "1" }} />,
    );

    expect(container).toMatchSnapshot();

    // Click on the button
    const btn = screen.getByRole("button");
    await user.click(btn);

    const dialog = await waitForDialog();
    expect(dialog).toBeInTheDocument();

    expect(mutationMock).not.toHaveBeenCalled();

    const input = screen.getByRole("textbox", { name: "Favorite label" });
    expect(input).toBeInTheDocument();

    const submitBtn = screen.getByRole("button", { name: "Save" });

    // Try to click without label. It should not trigger the mutation
    expect(submitBtn).toHaveAttribute("disabled", "");
    await user.click(submitBtn);
    expect(mutationMock).not.toHaveBeenCalled();

    // Type in the input the value of the name
    await user.type(input, "This is my favorite run");
    await user.click(submitBtn);

    expect(mutationMock).toHaveBeenCalledWith({
      variables: {
        input: {
          id: "1",
          label: "This is my favorite run",
          isFavorite: true,
        },
      },
    });

    // Dialog has been closed
    waitFor(() => {
      expect(dialog).not.toBeInTheDocument();
    });
  });

  it("asks for confirmation to remove it from the favorites", async () => {
    const user = userEvent.setup();

    mutationMock.mockReturnValue({ data: jest.fn() });
    const { container, debug } = render(
      <PipelineRunFavoriteTrigger run={{ isFavorite: true, id: "1" }} />,
    );

    // Click on the button
    const btn = screen.getByRole("button");

    confirmSpy.mockReturnValue(false);
    await user.click(btn);
    expect(mutationMock).not.toHaveBeenCalled();

    // User confirms
    confirmSpy.mockReturnValue(true);
    await user.click(btn);
    expect(confirmSpy).toHaveBeenCalled();
    expect(mutationMock).toHaveBeenCalledWith({
      variables: {
        input: {
          id: "1",
          isFavorite: false,
        },
      },
    });
  });
});
