import CountryBadge from "./CountryBadge";
import { render, screen } from "@testing-library/react";

describe("CountryBadge", () => {
  it("renders", async () => {
    const country = {
      code: "AE",
      flag: "https://api.demo.openhexa.org/static/flags/ae.gif",
      name: "United Arab Emirates",
    };
    const { container } = render(<CountryBadge country={country} />);
    expect(container).toMatchSnapshot();
    expect(screen.getByText(`${country.name}`)).toBeInTheDocument();
  });
});
