import { gql } from "@apollo/client";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "core/components/Table";
import { useTranslation } from "next-i18next";
import { PipelineVersionParametersTable_VersionFragment } from "./PipelineVersionParametersTable.generated";

type PipelineVersionParametersTableProps = {
  version: PipelineVersionParametersTable_VersionFragment;
};

const PipelineVersionParametersTable = (
  props: PipelineVersionParametersTableProps,
) => {
  const { version } = props;
  const { t } = useTranslation();
  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableCell spacing="tight" heading>
            {t("Name")}
          </TableCell>
          <TableCell spacing="tight" heading>
            {t("Code")}
          </TableCell>
          <TableCell spacing="tight" heading>
            {t("Type")}
          </TableCell>
          <TableCell spacing="tight" heading>
            {t("Required")}
          </TableCell>
          <TableCell spacing="tight" heading>
            {t("Multiple")}
          </TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {version.parameters.map((parameter) => (
          <TableRow key={parameter.code}>
            <TableCell spacing="tight" className="py-1">
              {parameter.name}
              &nbsp;<span className="text-gray-400">{parameter.help}</span>
            </TableCell>
            <TableCell spacing="tight" className="py-1">
              {parameter.code}
            </TableCell>
            <TableCell spacing="tight" className="py-1">
              <code>{parameter.type}</code>
            </TableCell>
            <TableCell spacing="tight" className="py-1">
              {parameter.required ? t("Yes") : t("No")}
            </TableCell>
            <TableCell spacing="tight" className="py-1">
              {parameter.multiple ? t("Yes") : t("No")}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

PipelineVersionParametersTable.fragments = {
  version: gql`
    fragment PipelineVersionParametersTable_version on PipelineVersion {
      id
      parameters {
        code
        name
        multiple
        type
        help
        required
        choices
      }
    }
  `,
};

export default PipelineVersionParametersTable;
