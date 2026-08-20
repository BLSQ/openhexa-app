import type { Geometry, Point } from "geojson";
import { isNumericValue } from "./format";

type Row = Record<string, unknown>;

/**
 * A map is selected by the names of the columns a query returns, the same way
 * charts are (see CHART_CONVENTIONS in ./chart). The `map_` prefix is what makes
 * it an opt-in: a table that happens to store `latitude` is not turned into a
 * map behind the author's back, and the alias states the intent in the query
 * itself. Only the columns a map plots have to be present — extra columns are
 * carried into the popup and stay readable in the table tab.
 *
 * Declaration order is the precedence when a query satisfies both.
 */
export const MAP_CONVENTIONS = [
  { kind: "latlon" as const, columns: ["map_latitude", "map_longitude"] },
  { kind: "geometry" as const, columns: ["map_geometry"] },
];

export const MAP_LATITUDE = "map_latitude";
export const MAP_LONGITUDE = "map_longitude";
export const MAP_GEOMETRY = "map_geometry";

/** The map is a preview, like the table: enough features to see the shape of
 * the data without handing the browser tens of thousands of layers to keep
 * alive. */
export const MAX_MAP_FEATURES = 2000;

export type MapSource =
  | { kind: "latlon"; latitude: string; longitude: string }
  | { kind: "geojson"; column: string }
  // Asked for as a map but not renderable as-is: PostGIS hands back WKB hex
  // unless the query converts it. Kept as its own kind rather than folded into
  // `null` so the UI can say what to do about it. The author aliased a column
  // to `map_geometry`, so silently falling back to a table would read as the
  // feature being broken.
  | { kind: "unreadable-geometry"; column: string };

export type MapFeature = {
  geometry: Geometry;
  properties: Row;
};

/** PostGIS renders geometry as (E)WKB hex when it is not converted: an even
 * number of hex digits, long enough that no realistic label collides with it. */
const WKB_HEX = /^[0-9A-Fa-f]{18,}$/;

const isWkbHex = (value: unknown): value is string =>
  typeof value === "string" &&
  value.length % 2 === 0 &&
  WKB_HEX.test(value.startsWith("\\x") ? value.slice(2) : value);

// Guards against coordinate columns holding something that is not a coordinate:
// an out-of-range value would place a marker nowhere, so the row is dropped.
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
 * How a result should be mapped, or null to fall back to the table. Column
 * names alone are not enough: a `map_latitude` column holding text is not a
 * coordinate, so the values are checked before committing to a map.
 */
export const detectMap = (columns: string[], rows: Row[]): MapSource | null => {
  if (rows.length === 0) {
    return null;
  }

  if (columns.includes(MAP_LATITUDE) && columns.includes(MAP_LONGITUDE)) {
    const plottable = rows.some((row) =>
      isValidLonLat(row[MAP_LONGITUDE], row[MAP_LATITUDE]),
    );
    if (plottable) {
      return {
        kind: "latlon",
        latitude: MAP_LATITUDE,
        longitude: MAP_LONGITUDE,
      };
    }
  }

  if (columns.includes(MAP_GEOMETRY)) {
    const present = rows.filter(
      (row) => row[MAP_GEOMETRY] !== null && row[MAP_GEOMETRY] !== undefined,
    );
    if (present.some((row) => parseGeometry(row[MAP_GEOMETRY]) !== null)) {
      return { kind: "geojson", column: MAP_GEOMETRY };
    }
    if (present.some((row) => isWkbHex(row[MAP_GEOMETRY]))) {
      return { kind: "unreadable-geometry", column: MAP_GEOMETRY };
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

/** Longitude/latitude corners, `[[west, south], [east, north]]` — the order
 * MapLibre's `fitBounds` takes, which is the reverse of GeoJSON's own
 * lat/lon-free convention being easy to flip by accident. */
export type MapBounds = [[number, number], [number, number]];

/**
 * The extent covering every feature, or null when none of them carries a usable
 * coordinate. Walks the coordinate arrays rather than switching on geometry
 * type: `[lon, lat]` positions are the leaves of every geometry GeoJSON
 * defines, so one recursion handles points, lines, polygons and their multi
 * variants — including positions that carry a third elevation value.
 *
 * Data straddling the antimeridian yields an extent spanning the globe. Leaflet
 * behaved the same way, and splitting the extent in two is only worth doing for
 * a dataset that actually crosses it.
 */
export const featuresBounds = (features: MapFeature[]): MapBounds | null => {
  let west = Infinity;
  let south = Infinity;
  let east = -Infinity;
  let north = -Infinity;

  const visit = (coordinates: unknown) => {
    if (!Array.isArray(coordinates)) {
      return;
    }
    if (
      typeof coordinates[0] === "number" &&
      typeof coordinates[1] === "number"
    ) {
      const [lon, lat] = coordinates;
      west = Math.min(west, lon);
      east = Math.max(east, lon);
      south = Math.min(south, lat);
      north = Math.max(north, lat);
      return;
    }
    for (const child of coordinates) {
      visit(child);
    }
  };

  for (const feature of features) {
    visit((feature.geometry as { coordinates?: unknown }).coordinates);
  }

  return west === Infinity
    ? null
    : [
        [west, south],
        [east, north],
      ];
};
