import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ResultsChart from "./ResultsChart";

// `useTranslation` is globally mocked to echo the key, so assertions target raw
// key strings and rendered structure rather than interpolated text.

const pieRows = [
  { pie_label: "Rapid test", pie_quantity: 75 },
  { pie_label: "PCR", pie_quantity: 25 },
];

describe("ResultsChart", () => {
  describe("bar", () => {
    const barRows = [
      { bar_label: "Gasabo", bar_quantity: 120 },
      { bar_label: "Kicukiro", bar_quantity: 80 },
    ];

    it("dims the other bars while one row is hovered", async () => {
      const { container } = render(<ResultsChart kind="bar" rows={barRows} />);
      const [gasabo, kicukiro] = Array.from(
        container.querySelectorAll<HTMLElement>("[style*='width']"),
      );

      await userEvent.hover(screen.getByText("Gasabo"));

      expect(gasabo).toHaveStyle({ opacity: "1" });
      expect(kicukiro).toHaveStyle({ opacity: "0.4" });

      await userEvent.unhover(screen.getByText("Gasabo"));
      expect(kicukiro).toHaveStyle({ opacity: "1" });
    });

    it("keeps the value beside the bar rather than in a tooltip", async () => {
      render(<ResultsChart kind="bar" rows={barRows} />);

      await userEvent.hover(screen.getByText("Gasabo"));

      expect(screen.getByText("120")).toBeInTheDocument();
      expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
    });
  });

  describe("line", () => {
    const lineRows = [
      { line_x: "2026-01", line_y: 10 },
      { line_x: "2026-02", line_y: 30 },
      { line_x: "2026-03", line_y: 20 },
    ];

    // The plot is laid out by the viewBox, which jsdom does not compute, so the
    // hit area is given a width for the pointer ratio to be resolved against.
    const hitArea = (container: HTMLElement) => {
      const rect = container.querySelector("rect")!;
      jest.spyOn(rect, "getBoundingClientRect").mockReturnValue({
        left: 0,
        width: 300,
      } as DOMRect);
      return rect;
    };

    it("names the point nearest the pointer", () => {
      const { container } = render(
        <ResultsChart kind="line" rows={lineRows} />,
      );
      const rect = hitArea(container);

      fireEvent.mouseMove(rect, { clientX: 150 });
      expect(screen.getByRole("tooltip")).toHaveTextContent("2026-02 30");

      fireEvent.mouseMove(rect, { clientX: 300 });
      expect(screen.getByRole("tooltip")).toHaveTextContent("2026-03 20");

      fireEvent.mouseLeave(rect);
      expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
    });

    it("marks the hovered point even where the standing markers are dropped", () => {
      // Past 40 points the per-point markers are not drawn, so the hover marker
      // is the only circle left and the guide is what locates it.
      const rows = Array.from({ length: 60 }, (_, index) => ({
        line_x: `p${index}`,
        line_y: index,
      }));
      const { container } = render(<ResultsChart kind="line" rows={rows} />);
      expect(container.querySelectorAll("circle")).toHaveLength(0);

      fireEvent.mouseMove(hitArea(container), { clientX: 0 });

      expect(container.querySelectorAll("circle")).toHaveLength(1);
      expect(
        container.querySelector("line[stroke-dasharray]"),
      ).toBeInTheDocument();
      expect(screen.getByRole("tooltip")).toHaveTextContent("p0 0");
    });
  });

  describe("pie", () => {
    const renderPie = (rows = pieRows) =>
      render(<ResultsChart kind="pie" rows={rows} />);

    const slices = (container: HTMLElement) =>
      Array.from(container.querySelectorAll("path"));

    it("draws one continuous slice per row", () => {
      const { container } = renderPie();
      expect(slices(container)).toHaveLength(2);
      // Wedges of background between slices read as holes, so the slices are
      // separated by a stroke and each one keeps its own full sweep.
      expect(slices(container)[0]).toHaveAttribute("stroke", "#ffffff");
    });

    it("draws a single row as a closed circle rather than an empty arc", () => {
      const { container } = renderPie([pieRows[0]]);
      const [only] = slices(container);
      // An arc whose endpoints coincide paints nothing: the full-turn case has
      // to be drawn as two half turns, so the path holds two arc commands.
      expect(only.getAttribute("d")?.match(/A /g)).toHaveLength(2);
      expect(only.getAttribute("d")).not.toContain(`M 100 100`);
    });

    it("names the hovered slice with its value and share, and dims the rest", async () => {
      const { container } = renderPie();
      const [rapid, pcr] = slices(container);

      await userEvent.hover(rapid);

      const tooltip = screen.getByRole("tooltip");
      expect(tooltip).toHaveTextContent("Rapid test");
      expect(tooltip).toHaveTextContent("75 (75.0%)");
      expect(rapid).toHaveStyle({ opacity: "1" });
      expect(pcr).toHaveStyle({ opacity: "0.4" });

      await userEvent.unhover(rapid);
      expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
    });

    it("highlights the matching slice when its legend row is hovered", async () => {
      const { container } = renderPie();

      await userEvent.hover(screen.getByText("PCR"));

      expect(screen.getByRole("tooltip")).toHaveTextContent("PCR");
      expect(slices(container)[0]).toHaveStyle({ opacity: "0.4" });
    });

    it("leaves out rows that cannot be a share of a whole", () => {
      renderPie([
        { pie_label: "Rapid test", pie_quantity: 75 },
        { pie_label: "Unknown", pie_quantity: 0 },
      ]);
      expect(screen.queryByText("Unknown")).not.toBeInTheDocument();
      expect(
        screen.getByText("{{count}} more rows not shown — see the Table tab."),
      ).toBeInTheDocument();
    });
  });
});
