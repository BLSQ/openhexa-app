import Time from "./Time";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { DateTime, Settings } from "luxon";

const nowMock = Settings.now as jest.Mock;

describe("Time", () => {
  it("renders the time in different formats", async () => {
    const dt = DateTime.local(2022, 2, 20, 10, 11, 34);
    Settings.defaultLocale = "en";
    const { container, rerender } = render(<Time datetime={dt.toISO()} />);
    expect(container).toMatchSnapshot();

    rerender(<Time datetime={dt.toISO()} format={DateTime.DATE_SHORT} />);
    expect(container).toMatchSnapshot();
  });

  it("renders relative time", async () => {
    const dt = DateTime.local(2022, 2, 20, 10, 11, 34);
    nowMock.mockReturnValue(dt.plus({ hours: 0, minutes: 10 }).toMillis());
    const { container, rerender } = render(
      <Time relative datetime={dt.toISO()} />
    );
    expect(container).toMatchSnapshot();

    nowMock.mockReturnValue(dt.plus({ hours: 2, minutes: 30 }).toMillis());
    rerender(<Time relative datetime={dt.toISO()} />);
    expect(container).toMatchSnapshot();
  });
});
