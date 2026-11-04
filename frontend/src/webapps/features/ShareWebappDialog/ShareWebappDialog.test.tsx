import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import { WebappType } from "graphql/types";
import ShareWebappDialog from "./ShareWebappDialog";

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
}));

const SERVE_URL = "http://my-app.webapps.localhost:8000/";

const renderDialog = (
  props: Partial<{
    isPublic: boolean;
    type: WebappType;
    onSave: (isPublic: boolean) => Promise<void>;
    onClose: () => void;
  }> = {},
) => {
  const onSave = props.onSave ?? jest.fn().mockResolvedValue(undefined);
  render(
    <TestApp mocks={[]}>
      <ShareWebappDialog
        open
        onClose={props.onClose ?? jest.fn()}
        onSave={onSave}
        webapp={{
          isPublic: props.isPublic ?? false,
          serveUrl: SERVE_URL,
          type: props.type ?? WebappType.Static,
        }}
      />
    </TestApp>,
  );
  return { onSave };
};

describe("ShareWebappDialog", () => {
  it("shows the link and the current audience", () => {
    renderDialog({ isPublic: false });

    expect(screen.getByText(SERVE_URL)).toBeInTheDocument();
    expect(screen.getByLabelText(/Workspace members/)).toBeChecked();
    expect(screen.getByLabelText(/Anyone with the link/)).not.toBeChecked();
    expect(screen.getByTestId("share-save")).toBeDisabled();
    expect(
      screen.getByText(/API requests run on behalf of the signed-in member/),
    ).toBeInTheDocument();
  });

  it("warns about API access when a static web app is opened to anyone", () => {
    renderDialog({ isPublic: false });

    fireEvent.click(screen.getByLabelText(/Anyone with the link/));

    expect(
      screen.getByText(/reach every public dataset, pipeline, file/),
    ).toBeInTheDocument();
    expect(screen.getByTestId("share-save")).toBeEnabled();
  });

  it("does not mention API access for iframe web apps", () => {
    renderDialog({ isPublic: false, type: WebappType.Iframe });

    fireEvent.click(screen.getByLabelText(/Anyone with the link/));

    expect(
      screen.queryByText(/reach every public dataset, pipeline, file/),
    ).not.toBeInTheDocument();
  });

  it("saves the chosen audience", async () => {
    const { onSave } = renderDialog({ isPublic: true });

    fireEvent.click(screen.getByLabelText(/Workspace members/));
    fireEvent.click(screen.getByTestId("share-save"));

    await waitFor(() => expect(onSave).toHaveBeenCalledWith(false));
  });
});
