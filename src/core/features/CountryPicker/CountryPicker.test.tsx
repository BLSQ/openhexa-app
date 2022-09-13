import CountryPicker from "./CountryPicker";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MockedProvider } from "@apollo/client/testing";

describe("CountryPicker", () => {
  it("renders", async () => {
    const onChange = jest.fn();

    const { container } = render(
      <MockedProvider mocks={[]}>
        <CountryPicker onChange={onChange} value={null} />
      </MockedProvider>
    );

    expect(container).toMatchSnapshot();
  });
});
