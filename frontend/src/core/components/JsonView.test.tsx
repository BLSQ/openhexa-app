import { render, screen } from "@testing-library/react";
import JsonView from "./JsonView";

describe("JsonView", () => {
  it("pretty-prints structured values", () => {
    const { container } = render(<JsonView value={{ a: 1, b: "two" }} />);
    expect(container.textContent).toContain("\"a\"");
    expect(container.textContent).toContain("two");
  });

  it("renders a raw string as plain text rather than quoted JSON", () => {
    render(<JsonView value="hello world" />);
    expect(screen.getByText("hello world")).toBeInTheDocument();
  });
});
