import clsx from "clsx";
import { isNumericValue, stringifyCellValue } from "./cellValue";

type Row = Record<string, unknown>;

type ResultsTableProps = {
  columns: string[];
  rows: Row[];
  /** Extra classes applied to every body cell of the named column. */
  columnClassName?: Record<string, string>;
};

const formatCell = (value: unknown) => {
  if (value === null || value === undefined) {
    return <span className="text-gray-300">NULL</span>;
  }
  return stringifyCellValue(value);
};

// Presentational grid shared by every successful result: a row-number gutter,
// a sticky header and one cell per column. Callers decide what to render (data
// rows, an EXPLAIN plan, …) and only tweak per-column styling through
// `columnClassName`, keeping this component free of result-type knowledge.
const ResultsTable = ({
  columns,
  rows,
  columnClassName,
}: ResultsTableProps) => (
  <div className="flex-1 overflow-auto">
    <table className="w-full border-separate border-spacing-0 text-sm">
      <thead className="sticky top-0 z-10 bg-gray-50">
        <tr>
          <th className="w-10 border-b border-gray-200 px-3 py-2 text-left text-xs font-semibold text-gray-400">
            #
          </th>
          {columns.map((column) => (
            <th
              key={column}
              className="border-b border-gray-200 px-3 py-2 text-left font-mono text-xs font-semibold text-gray-600"
            >
              {column}
            </th>
          ))}
          {/* Filler column absorbs the leftover width so the real columns stay
              sized to their content instead of stretching across the panel —
              this keeps right-aligned numbers next to their header when only a
              few columns are selected, while the header/row rules still span
              the full width. */}
          <th className="w-full border-b border-gray-200" aria-hidden />
        </tr>
      </thead>
      <tbody>
        {rows.map((row, rowIndex) => (
          <tr key={rowIndex} className="hover:bg-gray-50">
            <td className="border-b border-gray-100 px-3 py-1.5 text-right font-mono text-xs text-gray-400 select-none">
              {rowIndex + 1}
            </td>
            {columns.map((column) => {
              const value = row[column];
              return (
                <td
                  key={column}
                  className={clsx(
                    "border-b border-gray-100 px-3 py-1.5 text-gray-700",
                    isNumericValue(value) && "text-right font-mono",
                    columnClassName?.[column],
                  )}
                >
                  {formatCell(value)}
                </td>
              );
            })}
            <td className="border-b border-gray-100" aria-hidden />
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

export default ResultsTable;
