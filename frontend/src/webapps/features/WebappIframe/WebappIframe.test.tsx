import React from "react";
import { render, screen } from "@testing-library/react";
import WebappIframe from "./WebappIframe";

describe("WebappIframe", () => {
  it("⚠️ should not allow same origin iframe attribute for url of same origin", () => {
    const url = window.location.origin + "/some-path";
    render(<WebappIframe url={url} />);

    const iframe = screen.getByTestId("webapp-iframe");
    expect(iframe).toHaveAttribute(
      "sandbox",
      "allow-forms allow-popups allow-downloads allow-presentation allow-modals allow-scripts",
    );
    expect(iframe.getAttribute("sandbox")).not.toContain("allow-same-origin");
  });

  it("⚠️ exceptionally allows same origin iframe attribute for Superset dashboards", () => {
    const url =
      window.location.origin +
      "/superset/dashboard/f140a424-5817-4e07-a8fa-eab36257ea6e/";
    render(<WebappIframe url={url} />);

    const iframe = screen.getByTestId("webapp-iframe");
    expect(iframe).toHaveAttribute(
      "sandbox",
      "allow-forms allow-popups allow-downloads allow-presentation allow-modals allow-scripts allow-same-origin",
    );
  });

  it("should set sandbox permissions correctly for different origin url", () => {
    const url = "https://different-origin.com/some-path";
    render(<WebappIframe url={url} />);

    const iframe = screen.getByTestId("webapp-iframe");
    expect(iframe).toHaveAttribute(
      "sandbox",
      "allow-forms allow-popups allow-downloads allow-presentation allow-modals allow-scripts allow-same-origin",
    );
  });
});
