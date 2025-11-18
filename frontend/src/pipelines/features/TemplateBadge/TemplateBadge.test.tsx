import { render, screen } from "@testing-library/react";
import TemplateBadge from "./TemplateBadge";

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
}));

describe("TemplateBadge", () => {
  it("renders organization badge with logo when organization is provided and template is validated", () => {
    const organization = {
      name: "Test Organization",
      logo: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCI+PC9zdmc+",
    };

    render(
      <TemplateBadge
        organization={organization}
        validatedAt="2024-01-01T00:00:00Z"
      />
    );

    expect(screen.getByText("Test Organization")).toBeInTheDocument();
    const image = screen.getByAltText("Test Organization");
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute("src", organization.logo);
  });

  it("renders organization badge without logo when logo is null but template is validated", () => {
    const organization = {
      name: "Test Organization",
      logo: null,
    };

    render(
      <TemplateBadge
        organization={organization}
        validatedAt="2024-01-01T00:00:00Z"
      />
    );

    expect(screen.getByText("Test Organization")).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });

  it("renders Community badge when validatedAt is null even if organization is provided", () => {
    const organization = {
      name: "Test Organization",
      logo: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCI+PC9zdmc+",
    };

    render(<TemplateBadge organization={organization} validatedAt={null} />);

    expect(screen.getByText("Community")).toBeInTheDocument();
    expect(screen.queryByAltText("Test Organization")).not.toBeInTheDocument();
  });

  it("renders Community badge when organization is null", () => {
    render(<TemplateBadge organization={null} validatedAt={null} />);

    expect(screen.getByText("Community")).toBeInTheDocument();
  });

  it("renders Community badge when organization is undefined", () => {
    render(<TemplateBadge organization={undefined} validatedAt={null} />);

    expect(screen.getByText("Community")).toBeInTheDocument();
  });

  it("renders small size when size prop is sm", () => {
    const organization = {
      name: "Test Organization",
      logo: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCI+PC9zdmc+",
    };

    render(
      <TemplateBadge
        organization={organization}
        validatedAt="2024-01-01T00:00:00Z"
        size="sm"
      />
    );

    const image = screen.getByAltText("Test Organization");
    expect(image).toHaveClass("h-3.5", "w-3.5");

    const text = screen.getByText("Test Organization");
    expect(text).toHaveClass("text-xs");
  });

  it("renders medium size by default", () => {
    const organization = {
      name: "Test Organization",
      logo: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCI+PC9zdmc+",
    };

    render(
      <TemplateBadge
        organization={organization}
        validatedAt="2024-01-01T00:00:00Z"
      />
    );

    const image = screen.getByAltText("Test Organization");
    expect(image).toHaveClass("h-4", "w-4");

    const text = screen.getByText("Test Organization");
    expect(text).toHaveClass("text-sm");
  });

  it("hides icon when showIcon is false", () => {
    const organization = {
      name: "Test Organization",
      logo: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCI+PC9zdmc+",
    };

    render(
      <TemplateBadge
        organization={organization}
        validatedAt="2024-01-01T00:00:00Z"
        showIcon={false}
      />
    );

    expect(screen.getByText("Test Organization")).toBeInTheDocument();
    expect(screen.queryByAltText("Test Organization")).not.toBeInTheDocument();
  });

  it("renders Community badge with small size", () => {
    render(<TemplateBadge organization={null} size="sm" />);

    const text = screen.getByText("Community");
    expect(text).toHaveClass("text-xs");
  });
});
