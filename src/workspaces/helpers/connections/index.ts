import { ConnectionType } from "graphql/types";
export { convertFieldsToInput } from "./utils";
export type { ConnectionForm, FieldForm } from "./utils";

import postgresql from "./postgresql";
import { ConnectionDefinition } from "./utils";
import custom from "./custom";
import s3 from "./s3";
import gcs from "./gcs";
import iaso from "./iaso";
import dhis2 from "./dhis2";

const Connections: { [key in ConnectionType]: ConnectionDefinition } = {
  [ConnectionType.Postgresql]: postgresql,
  [ConnectionType.Custom]: custom,
  [ConnectionType.S3]: s3,
  [ConnectionType.Gcs]: gcs,
  [ConnectionType.Iaso]: iaso,
  [ConnectionType.Dhis2]: dhis2,
};

export default Connections;
