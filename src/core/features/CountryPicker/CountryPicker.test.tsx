import { MockedProvider } from "@apollo/client/testing";
import { render } from "@testing-library/react";
import CountryPicker from "./CountryPicker";

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
