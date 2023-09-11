import DatasourcePicker from "./DatasourcePicker";
import { render } from "@testing-library/react";

import { MockedProvider } from "@apollo/client/testing";

describe("DatasourcePicker", () => {
  it("renders", async () => {
    const onChange = jest.fn();

    const { container } = render(
      <MockedProvider mocks={[]}>
        <DatasourcePicker onChange={onChange} value={undefined} />
      </MockedProvider>,
    );
    expect(container).toMatchSnapshot();
  });
});
