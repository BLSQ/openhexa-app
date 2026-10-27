import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import { WebappType } from "graphql/types";
import MakeWebappPublicDialog from "./MakeWebappPublicDialog";

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
}));

const SERVE_URL = "http://my-app.webapps.localhost:8000/";

const renderDialog = (
  props: Partial<{
    onConfirm: () => Promise<void>;
    onClose: () => void;
    type: WebappType;
  }> = {},
) =>
  render(
    <TestApp mocks={[]}>
      <MakeWebappPublicDialog
        open
        onClose={props.onClose ?? jest.fn()}
        onConfirm={props.onConfirm ?? jest.fn().mockResolvedValue(undefined)}
        webapp={{ serveUrl: SERVE_URL, type: props.type ?? WebappType.Static }}
      />
    </TestApp>,
  );

describe("MakeWebappPublicDialog", () => {
  it("warns that anyone with the link can open the web app", () => {
    renderDialog();

    expect(
      screen.getByText(
        /Anyone with the link will be able to open this web app/,
      ),
    ).toBeInTheDocument();
  });

  it("shows the public link", () => {
    renderDialog();

    expect(screen.getByText("Public link")).toBeInTheDocument();
    expect(screen.getByText(SERVE_URL)).toBeInTheDocument();
  });

  it("explains what a static web app can reach once public", () => {
    renderDialog({ type: WebappType.Static });

    expect(
      screen.getByText(/reach every public dataset, pipeline, file/),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Make a resource public from its own page/),
    ).toBeInTheDocument();
  });

  it("skips the API explanation for non-static web apps", () => {
    renderDialog({ type: WebappType.Iframe });

    expect(
      screen.queryByText(/reach every public dataset, pipeline, file/),
    ).not.toBeInTheDocument();
  });

  it("confirms only when the user clicks make public", () => {
    const onConfirm = jest.fn().mockResolvedValue(undefined);
    const onClose = jest.fn();
    renderDialog({ onConfirm, onClose });

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onClose).toHaveBeenCalled();
    expect(onConfirm).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: "Make public" }));
    expect(onConfirm).toHaveBeenCalled();
  });

  it("disables the buttons while the confirmation is in progress", async () => {
    let resolve: () => void = () => {};
    const onConfirm = jest.fn(() => new Promise<void>((r) => (resolve = r)));
    renderDialog({ onConfirm });

    const confirmButton = screen.getByRole("button", { name: "Make public" });
    fireEvent.click(confirmButton);

    expect(confirmButton).toBeDisabled();
    expect(screen.getByRole("button", { name: "Cancel" })).toBeDisabled();

    resolve();
    await waitFor(() => expect(confirmButton).not.toBeDisabled());
  });
});
