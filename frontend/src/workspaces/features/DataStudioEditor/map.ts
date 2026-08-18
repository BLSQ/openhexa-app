import type { Geometry, Point } from "geojson";
import { isNumericValue } from "./format";

type Row = Record<string, unknown>;

/**
 * A result is drawn on a map when its columns name a geography, the same way
 * chart widgets are selected by column name: the query author opts in by what
 * they alias their columns to, and nothing else in the editor has to change.
 *
 * Matching is case-insensitive because column names reach us however the query
 * spelled them — the CPS monitoring tables return `Latitude`/`Longitude`, not
 * the lowercase form a hand-written query would use.
 */
const LATITUDE_NAMES = ["latitude", "lat"];
const LONGITUDE_NAMES = ["longitude", "lon", "lng", "long"];

/**
 * Geometry columns, in the spellings PostGIS tables use in practice.
 * `coordinates` is grouped here rather than with lat/lon: when a query returns a
 * single column of that name it holds a GeoJSON coordinate array, not a scalar.
 */
const GEOMETRY_NAMES = [
  "geometry",
  "geom",
  "simplified_geom",
  "the_geom",
  "coordinates",
];

/** The map is a preview, like the table: enough points to see the shape of the
 * data without handing the browser tens of thousands of layers to keep alive. */
export const MAX_MAP_FEATURES = 2000;

export type MapSource =
  | { kind: "latlon"; latitude: string; longitude: string }
  | { kind: "geojson"; column: string }
  // Detected as geography but not renderable as-is: PostGIS hands back WKB hex
  // unless the query converts it. Kept as its own kind rather than folded into
  // `null` so the UI can say what to do instead of silently showing a table.
  | { kind: "unreadable-geometry"; column: string };

export type MapFeature = {
  geometry: Geometry;
  properties: Row;
};

const findColumn = (columns: string[], names: string[]) =>
  columns.find((column) => names.includes(column.trim().toLowerCase()));

/** PostGIS renders geometry as (E)WKB hex when it is not converted: an even
 * number of hex digits, long enough that no realistic label collides with it. */
const WKB_HEX = /^[0-9A-Fa-f]{18,}$/;

const isWkbHex = (value: unknown): value is string =>
  typeof value === "string" &&
  value.length % 2 === 0 &&
  WKB_HEX.test(value.startsWith("\\x") ? value.slice(2) : value);

// Guards against a query that pairs two numeric columns which happen to be
// named like coordinates but hold something else: out-of-range values would
// place a marker nowhere, so the row is dropped instead.
const isValidLonLat = (lon: unknown, lat: unknown) =>
  isNumericValue(lon) &&
  isNumericValue(lat) &&
  Math.abs(Number(lat)) <= 90 &&
  Math.abs(Number(lon)) <= 180;

const isGeometryObject = (value: unknown): value is Geometry =>
  typeof value === "object" &&
  value !== null &&
  typeof (value as Geometry).type === "string" &&
  "coordinates" in value;

/**
 * The geometry a cell holds, or null when it cannot be read. Accepts what
 * `ST_AsGeoJSON` produces (a JSON string), what a JSON/JSONB column holds (an
 * object), and a bare coordinate pair — the three forms a query can return
 * without the backend having to convert anything.
 */
export const parseGeometry = (value: unknown): Geometry | null => {
  if (value === null || value === undefined) {
    return null;
  }
  if (isGeometryObject(value)) {
    return value;
  }
  if (Array.isArray(value)) {
    return isValidLonLat(value[0], value[1])
      ? { type: "Point", coordinates: [Number(value[0]), Number(value[1])] }
      : null;
  }
  if (typeof value !== "string") {
    return null;
  }
  try {
    return parseGeometry(JSON.parse(value));
  } catch {
    return null;
  }
};

/**
 * How a result should be mapped, or null to leave it as a table. Column names
 * alone are not enough: a `geom` column still holding WKB cannot be drawn, and
 * a `lat`/`lon` pair of text columns is not a geography, so the values are
 * checked before committing to a map.
 */
export const detectMap = (columns: string[], rows: Row[]): MapSource | null => {
  if (rows.length === 0) {
    return null;
  }

  const latitude = findColumn(columns, LATITUDE_NAMES);
  const longitude = findColumn(columns, LONGITUDE_NAMES);
  if (latitude && longitude) {
    const plottable = rows.some((row) =>
      isValidLonLat(row[longitude], row[latitude]),
    );
    if (plottable) {
      return { kind: "latlon", latitude, longitude };
    }
  }

  const geometry = findColumn(columns, GEOMETRY_NAMES);
  if (geometry) {
    const present = rows.filter(
      (row) => row[geometry] !== null && row[geometry] !== undefined,
    );
    if (present.some((row) => parseGeometry(row[geometry]) !== null)) {
      return { kind: "geojson", column: geometry };
    }
    if (present.some((row) => isWkbHex(row[geometry]))) {
      return { kind: "unreadable-geometry", column: geometry };
    }
  }

  return null;
};

/**
 * Turn result rows into map features, preserving the order the query returned
 * them in. Rows whose geography cannot be read are dropped rather than guessed
 * at — the table tab still shows them in full.
 *
 * The geography columns are kept out of `properties`: a popup listing the raw
 * coordinates the marker is already positioned by is noise, and a WKB blob in a
 * popup is worse than noise.
 */
export const toFeatures = (
  source: MapSource,
  rows: Row[],
  limit = MAX_MAP_FEATURES,
): { features: MapFeature[]; hidden: number } => {
  if (source.kind === "unreadable-geometry") {
    return { features: [], hidden: 0 };
  }

  const geographyColumns =
    source.kind === "latlon"
      ? [source.latitude, source.longitude]
      : [source.column];

  const features: MapFeature[] = [];
  let hidden = 0;

  for (const row of rows) {
    const geometry =
      source.kind === "latlon"
        ? isValidLonLat(row[source.longitude], row[source.latitude])
          ? ({
              type: "Point",
              coordinates: [
                Number(row[source.longitude]),
                Number(row[source.latitude]),
              ],
            } as Point)
          : null
        : parseGeometry(row[source.column]);

    if (!geometry) {
      continue;
    }
    if (features.length >= limit) {
      hidden += 1;
      continue;
    }

    const properties: Row = {};
    for (const [key, value] of Object.entries(row)) {
      if (!geographyColumns.includes(key)) {
        properties[key] = value;
      }
    }
    features.push({ geometry, properties });
  }

  return { features, hidden };
};
