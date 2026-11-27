import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import SecretField from "./SecretField";

describe("SecretField", () => {
  it("masks the secret by default and marks the revealed container as data-mp-no-record", async () => {
    const user = userEvent.setup();
    const { container } = render(
      <TestApp mocks={[]}>
        <SecretField value="super-secret-password" />
      </TestApp>,
    );

    expect(screen.getByText("*********")).toBeInTheDocument();
    expect(screen.queryByText("super-secret-password")).not.toBeInTheDocument();
    expect(container.querySelector("[data-mp-no-record]")).toBeNull();

    const [toggleButton] = screen.getAllByRole("button");
    await user.click(toggleButton);

    const revealed = screen.getByText("super-secret-password");
    expect(revealed).toBeInTheDocument();
    expect(revealed.closest("[data-mp-no-record]")).not.toBeNull();

    const [hideButton] = screen.getAllByRole("button");
    await user.click(hideButton);

    expect(screen.getByText("*********")).toBeInTheDocument();
    expect(screen.queryByText("super-secret-password")).not.toBeInTheDocument();
    expect(container.querySelector("[data-mp-no-record]")).toBeNull();
  });
});
