import Checkbox from "core/components/forms/Checkbox";
import { Hooks } from "react-table";

export interface UseCheckboxColumn<D extends object = {}> {
  (hooks: Hooks<D>): void;
}

export const useCheckboxColumn: UseCheckboxColumn = (hooks) => {
  hooks.visibleColumns.push((columns) => [
    // Let's make a column for selection
    {
      id: "selection",
      width: 35,

      // The header can use the table's getToggleAllRowsSelectedProps method
      // to render a checkbox
      Header: ({ getToggleAllPageRowsSelectedProps }) => (
        <Checkbox {...getToggleAllPageRowsSelectedProps()} />
      ),
      // The cell can use the individual row's getToggleRowSelectedProps method
      // to the render a checkbox
      Cell: (cell) => <Checkbox {...cell.row.getToggleRowSelectedProps()} />,
    },
    ...columns,
  ]);
};
