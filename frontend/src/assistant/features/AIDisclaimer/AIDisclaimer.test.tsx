import { render, screen } from "@testing-library/react";
import { ReactNode } from "react";
import AIDisclaimer, { AI_DOCS_URL } from "./index";

jest.mock("next-i18next", () => ({
  Trans: ({ children }: { children: ReactNode }) => <>{children}</>,
}));

describe("AIDisclaimer", () => {
  it("links the legend to the AI documentation page in a new tab", () => {
    render(<AIDisclaimer />);

    expect(
      screen.getByText(
        /AI can make mistakes\. Always verify important information\./,
      ),
    ).toBeInTheDocument();
    const link = screen.getByRole("link", {
      name: "Learn how AI is used in OpenHEXA",
    });
    expect(link).toHaveAttribute("href", AI_DOCS_URL);
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noopener noreferrer");
  });
});
