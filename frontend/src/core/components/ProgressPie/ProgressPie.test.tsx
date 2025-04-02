import { render } from "@testing-library/react";
import ProgressPie from "./ProgressPie";

describe("ProgressPie", () => {
  it("renders a progress pie at different progress states", async () => {
    const { container, rerender } = render(<ProgressPie progress={0} />);
    expect(container).toMatchSnapshot();

    rerender(<ProgressPie progress={50} />);
    expect(container).toMatchSnapshot();

    rerender(<ProgressPie progress={100} />);
    expect(container).toMatchSnapshot();
  });

  it("accepts a different set of colours", () => {
    const { container } = render(
      <ProgressPie
        progress={30}
        background="text-teal-500"
        foreground="text-teal-700"
      />,
    );

    expect(container.getElementsByClassName("text-teal-500").length).toEqual(1);
    expect(container.getElementsByClassName("text-teal-700").length).toEqual(1);
  });
});
