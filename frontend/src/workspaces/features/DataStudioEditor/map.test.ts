import { detectMap, parseGeometry, toFeatures } from "./map";

// A single Abidjan point, as PostGIS returns it from ST_AsGeoJSON.
const GEOJSON_POINT = '{"type":"Point","coordinates":[-4.02,5.34]}';

// ST_AsBinary/raw geometry output: EWKB hex for the same point.
const WKB_POINT = "0101000020E6100000B81E85EB51101040295C8FC2F5A81440";

describe("detectMap", () => {
  it("maps a map_latitude/map_longitude pair", () => {
    expect(
      detectMap(
        ["name", "map_latitude", "map_longitude"],
        [{ name: "Diogo", map_latitude: 5.34, map_longitude: -4.02 }],
      ),
    ).toEqual({
      kind: "latlon",
      latitude: "map_latitude",
      longitude: "map_longitude",
    });
  });

  it("reads numeric strings, which is how NUMERIC columns arrive", () => {
    expect(
      detectMap(
        ["map_latitude", "map_longitude"],
        [{ map_latitude: "5.34", map_longitude: "-4.02" }],
      ),
    ).not.toBeNull();
  });

  it("ignores a coordinate pair holding text", () => {
    expect(
      detectMap(
        ["map_latitude", "map_longitude"],
        [{ map_latitude: "north", map_longitude: "west" }],
      ),
    ).toBeNull();
  });

  it("ignores coordinates outside the world, which cannot be a geography", () => {
    expect(
      detectMap(
        ["map_latitude", "map_longitude"],
        [{ map_latitude: 950, map_longitude: -4 }],
      ),
    ).toBeNull();
  });

  it("maps a geometry column converted to GeoJSON", () => {
    expect(
      detectMap(["map_geometry"], [{ map_geometry: GEOJSON_POINT }]),
    ).toEqual({
      kind: "geojson",
      column: "map_geometry",
    });
  });

  it("does not map a geography column that was not aliased to the convention", () => {
    expect(
      detectMap(
        ["latitude", "longitude"],
        [{ latitude: 5.34, longitude: -4.02 }],
      ),
    ).toBeNull();
    expect(detectMap(["geom"], [{ geom: GEOJSON_POINT }])).toBeNull();
  });

  it("reports an unconverted geometry column rather than giving up silently", () => {
    expect(detectMap(["map_geometry"], [{ map_geometry: WKB_POINT }])).toEqual({
      kind: "unreadable-geometry",
      column: "map_geometry",
    });
  });

  it("prefers the coordinate pair when a result carries both conventions", () => {
    expect(
      detectMap(
        ["map_latitude", "map_longitude", "map_geometry"],
        [
          {
            map_latitude: 5.34,
            map_longitude: -4.02,
            map_geometry: GEOJSON_POINT,
          },
        ],
      ),
    ).toEqual({
      kind: "latlon",
      latitude: "map_latitude",
      longitude: "map_longitude",
    });
  });

  it("leaves an ordinary result as a table", () => {
    expect(
      detectMap(["district", "cases"], [{ district: "A", cases: 3 }]),
    ).toBe(null);
  });

  it("does not map an empty result", () => {
    expect(detectMap(["map_latitude", "map_longitude"], [])).toBeNull();
  });
});

describe("parseGeometry", () => {
  it("reads the JSON string ST_AsGeoJSON produces", () => {
    expect(parseGeometry(GEOJSON_POINT)).toEqual({
      type: "Point",
      coordinates: [-4.02, 5.34],
    });
  });

  it("reads a geometry a JSONB column already returns as an object", () => {
    const geometry = { type: "Polygon", coordinates: [[[0, 0]]] };
    expect(parseGeometry(geometry)).toEqual(geometry);
  });

  it("reads a bare coordinate pair as a point", () => {
    expect(parseGeometry([-4.02, 5.34])).toEqual({
      type: "Point",
      coordinates: [-4.02, 5.34],
    });
  });

  it.each([null, undefined, "", "not json", WKB_POINT, 42])(
    "returns null for %p",
    (value) => {
      expect(parseGeometry(value)).toBeNull();
    },
  );
});

describe("toFeatures", () => {
  const source = {
    kind: "latlon" as const,
    latitude: "map_latitude",
    longitude: "map_longitude",
  };

  it("places points at [longitude, latitude], the GeoJSON axis order", () => {
    const { features } = toFeatures(source, [
      { map_latitude: 5.34, map_longitude: -4.02 },
    ]);
    expect(features[0].geometry).toEqual({
      type: "Point",
      coordinates: [-4.02, 5.34],
    });
  });

  it("keeps the query's row order, which is the intended reading order", () => {
    const { features } = toFeatures(source, [
      { map_latitude: 1, map_longitude: 1, name: "first" },
      { map_latitude: 2, map_longitude: 2, name: "second" },
    ]);
    expect(features.map((feature) => feature.properties.name)).toEqual([
      "first",
      "second",
    ]);
  });

  it("carries the other columns as properties for the popup", () => {
    const { features } = toFeatures(source, [
      {
        map_latitude: 5.34,
        map_longitude: -4.02,
        district: "Boundiali",
        cases: 12,
      },
    ]);
    expect(features[0].properties).toEqual({
      district: "Boundiali",
      cases: 12,
    });
  });

  it("leaves the coordinate columns out of the popup, which the marker already shows", () => {
    const { features } = toFeatures(source, [
      { map_latitude: 5.34, map_longitude: -4.02, name: "Diogo" },
    ]);
    expect(features[0].properties).not.toHaveProperty("map_latitude");
    expect(features[0].properties).not.toHaveProperty("map_longitude");
  });

  it("drops rows with no usable location instead of guessing at one", () => {
    const { features } = toFeatures(source, [
      { map_latitude: 5.34, map_longitude: -4.02 },
      { map_latitude: null, map_longitude: null },
      { map_latitude: "n/a", map_longitude: "n/a" },
    ]);
    expect(features).toHaveLength(1);
  });

  it("caps the features and reports how many were left off", () => {
    const rows = Array.from({ length: 5 }, () => ({
      map_latitude: 5.34,
      map_longitude: -4.02,
    }));
    expect(toFeatures(source, rows, 2)).toMatchObject({ hidden: 3 });
  });

  it("returns nothing for a geometry it cannot read", () => {
    expect(
      toFeatures({ kind: "unreadable-geometry", column: "map_geometry" }, [
        { map_geometry: WKB_POINT },
      ]),
    ).toEqual({ features: [], hidden: 0 });
  });
});
