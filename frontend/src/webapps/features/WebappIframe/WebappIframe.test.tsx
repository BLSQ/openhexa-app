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

  it("should block javascript: protocol URLs", () => {
    const consoleWarnSpy = jest.spyOn(console, "warn").mockImplementation();
    const url = "javascript:alert('xss')";
    render(<WebappIframe url={url} />);

    const iframe = screen.getByTestId("webapp-iframe");
    expect(iframe).toHaveAttribute("src", "");
    expect(consoleWarnSpy).toHaveBeenCalledWith(
      "Blocked unsafe URL protocol: javascript:",
    );
    consoleWarnSpy.mockRestore();
  });

  it("should block data: protocol URLs", () => {
    const consoleWarnSpy = jest.spyOn(console, "warn").mockImplementation();
    const url = "data:text/html,<script>alert('xss')</script>";
    render(<WebappIframe url={url} />);

    const iframe = screen.getByTestId("webapp-iframe");
    expect(iframe).toHaveAttribute("src", "");
    expect(consoleWarnSpy).toHaveBeenCalledWith(
      "Blocked unsafe URL protocol: data:",
    );
    consoleWarnSpy.mockRestore();
  });

  it("should block vbscript: protocol URLs", () => {
    const consoleWarnSpy = jest.spyOn(console, "warn").mockImplementation();
    const url = "vbscript:msgbox('xss')";
    render(<WebappIframe url={url} />);

    const iframe = screen.getByTestId("webapp-iframe");
    expect(iframe).toHaveAttribute("src", "");
    expect(consoleWarnSpy).toHaveBeenCalledWith(
      "Blocked unsafe URL protocol: vbscript:",
    );
    consoleWarnSpy.mockRestore();
  });

  it("should allow valid HTTPS URLs", () => {
    const url = "https://example.com/webapp";
    render(<WebappIframe url={url} />);

    const iframe = screen.getByTestId("webapp-iframe");
    expect(iframe).toHaveAttribute("src", url);
  });

  it("should allow valid HTTP URLs", () => {
    const url = "http://example.com/webapp";
    render(<WebappIframe url={url} />);

    const iframe = screen.getByTestId("webapp-iframe");
    expect(iframe).toHaveAttribute("src", url);
  });

  it("should allow relative URLs", () => {
    const url = "/workspace/webapp/path";
    render(<WebappIframe url={url} />);

    const iframe = screen.getByTestId("webapp-iframe");
    expect(iframe).toHaveAttribute("src", url);
  });

  it("should handle empty or invalid URLs", () => {
    render(<WebappIframe url="" />);

    const iframe = screen.getByTestId("webapp-iframe");
    expect(iframe).toHaveAttribute("src", "");
  });
});
