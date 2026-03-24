import React from "react";
import { render, screen } from "@testing-library/react";
import WebappIframe from "./WebappIframe";
import { WebappType } from "graphql/types";

const BASE_SANDBOX =
  "allow-forms allow-popups allow-downloads allow-presentation allow-modals allow-scripts";

describe("WebappIframe", () => {
  it("⚠️ should not allow same origin iframe attribute for url of same origin", () => {
    const url = window.location.origin + "/some-path";
    render(<WebappIframe url={url} />);

    const iframe = screen.getByTestId("webapp-iframe");
    expect(iframe).toHaveAttribute("sandbox", BASE_SANDBOX);
    expect(iframe.getAttribute("sandbox")).not.toContain("allow-same-origin");
  });

  it("⚠️ should never allow same origin for static webapps even on a different origin", () => {
    const url = "https://api.example.com/webapps/some-id/";
    render(<WebappIframe url={url} type={WebappType.Static} />);

    const iframe = screen.getByTestId("webapp-iframe");
    expect(iframe).toHaveAttribute("sandbox", BASE_SANDBOX);
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
      `${BASE_SANDBOX} allow-same-origin`,
    );
  });

  it("should set sandbox permissions correctly for different origin url", () => {
    const url = "https://different-origin.com/some-path";
    render(<WebappIframe url={url} />);

    const iframe = screen.getByTestId("webapp-iframe");
    expect(iframe).toHaveAttribute(
      "sandbox",
      `${BASE_SANDBOX} allow-same-origin`,
    );
  });

  it("should allow same origin for iframe type webapps on different origin", () => {
    const url = "https://external-app.com/dashboard";
    render(<WebappIframe url={url} type={WebappType.Iframe} />);

    const iframe = screen.getByTestId("webapp-iframe");
    expect(iframe).toHaveAttribute(
      "sandbox",
      `${BASE_SANDBOX} allow-same-origin`,
    );
  });
});
