import CountryPicker from "./CountryPicker";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MockedProvider } from "@apollo/client/testing";

describe("CountryPicker", () => {
  it("renders", async () => {
    const onChange = jest.fn();

    const { container, debug } = render(
      <MockedProvider mocks={[]}>
        <CountryPicker onChange={onChange} value={undefined} />
      </MockedProvider>,
    );
    expect(container).toMatchSnapshot();
  });
});
