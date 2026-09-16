import { ChartBarIcon } from "@heroicons/react/24/outline";
import Tooltip from "core/components/Tooltip";
import { useTranslation } from "next-i18next";
import { SQL_WIDGETS_DOCS_URL } from "workspaces/helpers/dataStudio";
import { ChartKind, CHART_CONVENTIONS } from "./chart";
import { MAP_CONVENTIONS } from "./map";

type MapKind = (typeof MAP_CONVENTIONS)[number]["kind"];

const WidgetHint = () => {
  const { t } = useTranslation();

  // The same keys the widgets use for their own accessible names, so a widget
  // type is not named two different ways in two places.
  const kindLabels: Record<ChartKind, string> = {
    bar: t("Bar chart"),
    line: t("Line chart"),
    pie: t("Pie chart"),
  };

  const mapLabels: Record<MapKind, string> = {
    latlon: t("Point map"),
    geometry: t("Shape map"),
  };

  // Charts and maps are one convention family to the reader — both are "name
  // your columns this way and the result is drawn" — so they share one list,
  // in the order the detection tries them.
  const conventions = [
    ...CHART_CONVENTIONS.map((convention) => ({
      key: convention.kind as string,
      columns: [convention.label, convention.value],
      label: kindLabels[convention.kind],
    })),
    ...MAP_CONVENTIONS.map((convention) => ({
      key: convention.kind as string,
      columns: convention.columns,
      label: mapLabels[convention.kind],
    })),
  ];

  return (
    <Tooltip
      placement="top"
      label={
        <div className="break-normal">
          <p className="mb-1.5 font-medium text-gray-700">
            {t("Turn a result into a chart or a map")}
          </p>
          <p className="mb-1.5">
            {t(
              "Alias your columns to one of these sets and the result is drawn, with the table one tab away:",
            )}
          </p>
          <ul className="space-y-0.5">
            {conventions.map((convention) => (
              <li
                key={convention.key}
                className="flex items-baseline justify-between gap-4 whitespace-nowrap"
              >
                <span className="font-mono text-gray-700">
                  {convention.columns.join(", ")}
                </span>
                <span className="text-gray-400">{convention.label}</span>
              </li>
            ))}
          </ul>
          <p className="mt-1.5 text-gray-400">
            {t("Click to read the guide.")}
          </p>
        </div>
      }
      renderTrigger={(ref) => (
        // The trigger is itself the link to the guide, so the tooltip never has
        // to be made interactive for the user to reach the documentation.
        <span ref={ref}>
          <a
            href={SQL_WIDGETS_DOCS_URL}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1 text-blue-600 hover:text-blue-500"
          >
            <ChartBarIcon className="h-3.5 w-3.5 shrink-0" />
            {t("Visualize this result")}
          </a>
        </span>
      )}
    />
  );
};

export default WidgetHint;
