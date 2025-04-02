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
  className?: string;
};

const PipelineVersionParametersTable = ({
  version,
  className,
}: PipelineVersionParametersTableProps) => {
  const { t } = useTranslation();
  return (
    <Table className={className}>
      <TableHead>
        <TableRow>
          <TableCell heading>{t("Name")}</TableCell>
          <TableCell heading>{t("Code")}</TableCell>
          <TableCell heading>{t("Type")}</TableCell>
          <TableCell heading>{t("Required")}</TableCell>
          <TableCell heading>{t("Multiple")}</TableCell>
          <TableCell heading>{t("Default value")}</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {version.parameters.map((parameter, i) => (
          <TableRow key={i}>
            <TableCell className="py-1">
              {parameter.name}
              &nbsp;<span className="text-gray-400">{parameter.help}</span>
            </TableCell>
            <TableCell className="py-1">{parameter.code}</TableCell>
            <TableCell className="py-1">
              <code>{parameter.type}</code>
            </TableCell>
            <TableCell className="py-1">
              {parameter.required ? t("Yes") : t("No")}
            </TableCell>
            <TableCell className="py-1">
              {parameter.multiple ? t("Yes") : t("No")}
            </TableCell>
            <TableCell className="py-1">
              {(version.config && version.config[parameter.code]?.toString()) ||
                "-"}
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
      config
    }
  `,
};

export default PipelineVersionParametersTable;
