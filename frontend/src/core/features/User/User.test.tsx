import User from "./User";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const USER = {
  displayName: "Test User",
  email: "testuser@openhexa.org",
  id: "UUID",
  avatar: {
    initials: "TU",
    color: "",
  },
};

describe("User", () => {
  it("renders", async () => {
    const { container } = render(<User user={USER} />);
    expect(screen.queryByText(USER.email)).toBeNull();
    expect(container).toMatchSnapshot();
  });

  it("renders with the subtext", () => {
    const { container } = render(<User user={USER} subtext />);
    expect(screen.getByText(USER.email)).toBeInTheDocument();
    expect(container).toMatchSnapshot();
  });
});
