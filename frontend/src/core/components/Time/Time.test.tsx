import { render, screen } from "@testing-library/react";
import { DateTime, Settings } from "luxon";
import Time from "./Time";

const nowMock = Settings.now as jest.Mock;

describe("Time", () => {
  it("renders the time in different formats", async () => {
    const dt = DateTime.local(2022, 2, 20, 10, 11, 34);
    Settings.defaultLocale = "en";
    render(<Time datetime={dt.toISO()!} />);
    expect(screen.getByText("2/20/2022, 10:11 AM")).toBeInTheDocument();
  });

  it("treats a datetime without offset as UTC", async () => {
    Settings.defaultLocale = "en";
    const expected = DateTime.fromISO("2022-02-20T10:11:34Z")
      .toLocal()
      .toLocaleString(DateTime.DATETIME_SHORT_WITH_SECONDS);
    render(
      <Time
        datetime="2022-02-20T10:11:34.123456"
        format={DateTime.DATETIME_SHORT_WITH_SECONDS}
      />,
    );
    expect(screen.getByText(expected)).toBeInTheDocument();
  });

  it("renders relative time", async () => {
    const dt = DateTime.local(2022, 2, 20, 10, 11, 34);
    nowMock.mockReturnValue(dt.plus({ hours: 0, minutes: 10 }).toMillis());
    const { rerender } = render(<Time relative datetime={dt.toISO()!} />);
    expect(screen.getByText("10 minutes ago")).toBeInTheDocument();
    nowMock.mockReturnValue(dt.plus({ hours: 2, minutes: 30 }).toMillis());
    rerender(<Time relative datetime={dt.toISO()!} />);
    expect(screen.getByText("2 hours ago")).toBeInTheDocument();
  });
});
