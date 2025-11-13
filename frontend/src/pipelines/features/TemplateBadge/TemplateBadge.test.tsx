import { render, screen } from "@testing-library/react";
import TemplateBadge from "./TemplateBadge";

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
}));

describe("TemplateBadge", () => {
  it("renders Bluesquare badge with icon when publisher is Bluesquare", () => {
    render(<TemplateBadge publisher="Bluesquare" />);

    expect(screen.getByText("Bluesquare")).toBeInTheDocument();
    const image = screen.getByAltText("Bluesquare");
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute("src", "/images/bluesquare-icon.svg");
  });

  it("renders Community badge when publisher is Community", () => {
    render(<TemplateBadge publisher="Community" />);

    expect(screen.getByText("Community")).toBeInTheDocument();
    expect(screen.queryByAltText("Bluesquare")).not.toBeInTheDocument();
  });

  it("renders Community badge when publisher is null", () => {
    render(<TemplateBadge publisher={null} />);

    expect(screen.getByText("Community")).toBeInTheDocument();
  });

  it("renders Community badge when publisher is undefined", () => {
    render(<TemplateBadge publisher={undefined} />);

    expect(screen.getByText("Community")).toBeInTheDocument();
  });

  it("renders small size when size prop is sm", () => {
    render(<TemplateBadge publisher="Bluesquare" size="sm" />);

    const image = screen.getByAltText("Bluesquare");
    expect(image).toHaveClass("h-3.5", "w-3.5");

    const text = screen.getByText("Bluesquare");
    expect(text).toHaveClass("text-xs");
  });

  it("renders medium size by default", () => {
    render(<TemplateBadge publisher="Bluesquare" />);

    const image = screen.getByAltText("Bluesquare");
    expect(image).toHaveClass("h-4", "w-4");

    const text = screen.getByText("Bluesquare");
    expect(text).toHaveClass("text-sm");
  });

  it("hides icon when showIcon is false", () => {
    render(<TemplateBadge publisher="Bluesquare" showIcon={false} />);

    expect(screen.getByText("Bluesquare")).toBeInTheDocument();
    expect(screen.queryByAltText("Bluesquare")).not.toBeInTheDocument();
  });

  it("renders Community badge with small size", () => {
    render(<TemplateBadge publisher="Community" size="sm" />);

    const text = screen.getByText("Community");
    expect(text).toHaveClass("text-xs");
  });
});
