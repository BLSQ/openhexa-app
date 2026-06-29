import { render } from "@testing-library/react";
import RendererBoundary from "./RendererBoundary";

function Boom(): JSX.Element {
  throw new Error("renderer blew up on an unexpected shape");
}

describe("RendererBoundary", () => {
  it("falls back to raw JSON when a renderer throws", () => {
    // React logs the caught error; silence it to keep test output clean.
    const spy = jest.spyOn(console, "error").mockImplementation(() => {});
    const { container } = render(
      <RendererBoundary value={{ kept: "value" }}>
        <Boom />
      </RendererBoundary>,
    );
    expect(container.textContent).toContain("kept");
    expect(container.textContent).toContain("value");
    spy.mockRestore();
  });

  it("renders children unchanged when they do not throw", () => {
    const { getByText } = render(
      <RendererBoundary value={{}}>
        <span>all good</span>
      </RendererBoundary>,
    );
    expect(getByText("all good")).toBeInTheDocument();
  });
});
