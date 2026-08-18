import { detectMap, parseGeometry, toFeatures } from "./map";

// A single Abidjan point, as PostGIS returns it from ST_AsGeoJSON.
const GEOJSON_POINT = '{"type":"Point","coordinates":[-4.02,5.34]}';

// ST_AsBinary/raw geometry output: EWKB hex for the same point.
const WKB_POINT = "0101000020E6100000B81E85EB51101040295C8FC2F5A81440";

describe("detectMap", () => {
  it("maps a latitude/longitude pair", () => {
    expect(
      detectMap(
        ["name", "latitude", "longitude"],
        [{ name: "Diogo", latitude: 5.34, longitude: -4.02 }],
      ),
    ).toEqual({ kind: "latlon", latitude: "latitude", longitude: "longitude" });
  });

  it("matches column names whatever their case, as the source tables spell them", () => {
    expect(
      detectMap(
        ["Latitude", "Longitude"],
        [{ Latitude: 5.34, Longitude: -4.02 }],
      ),
    ).toEqual({ kind: "latlon", latitude: "Latitude", longitude: "Longitude" });
  });

  it("accepts the short spellings", () => {
    expect(detectMap(["lat", "lng"], [{ lat: 5.34, lng: -4.02 }])).toEqual({
      kind: "latlon",
      latitude: "lat",
      longitude: "lng",
    });
  });

  it("reads numeric strings, which is how NUMERIC columns arrive", () => {
    expect(
      detectMap(
        ["latitude", "longitude"],
        [{ latitude: "5.34", longitude: "-4.02" }],
      ),
    ).not.toBeNull();
  });

  it("ignores a latitude/longitude pair holding text", () => {
    expect(
      detectMap(
        ["latitude", "longitude"],
        [{ latitude: "north", longitude: "west" }],
      ),
    ).toBeNull();
  });

  it("ignores coordinates outside the world, which cannot be a geography", () => {
    expect(
      detectMap(["latitude", "longitude"], [{ latitude: 950, longitude: -4 }]),
    ).toBeNull();
  });

  it("maps a geometry column converted to GeoJSON", () => {
    expect(detectMap(["geom"], [{ geom: GEOJSON_POINT }])).toEqual({
      kind: "geojson",
      column: "geom",
    });
  });

  it.each(["geometry", "geom", "simplified_geom", "the_geom", "coordinates"])(
    "recognises the %s column name",
    (column) => {
      expect(detectMap([column], [{ [column]: GEOJSON_POINT }])).toEqual({
        kind: "geojson",
        column,
      });
    },
  );

  it("reports an unconverted geometry column rather than giving up silently", () => {
    expect(detectMap(["geom"], [{ geom: WKB_POINT }])).toEqual({
      kind: "unreadable-geometry",
      column: "geom",
    });
  });

  it("prefers the latitude/longitude pair when a result carries both", () => {
    expect(
      detectMap(
        ["latitude", "longitude", "geom"],
        [{ latitude: 5.34, longitude: -4.02, geom: GEOJSON_POINT }],
      ),
    ).toEqual({ kind: "latlon", latitude: "latitude", longitude: "longitude" });
  });

  it("leaves an ordinary result as a table", () => {
    expect(
      detectMap(["district", "cases"], [{ district: "A", cases: 3 }]),
    ).toBe(null);
  });

  it("does not map an empty result", () => {
    expect(detectMap(["latitude", "longitude"], [])).toBeNull();
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
    latitude: "latitude",
    longitude: "longitude",
  };

  it("places points at [longitude, latitude], the GeoJSON axis order", () => {
    const { features } = toFeatures(source, [
      { latitude: 5.34, longitude: -4.02 },
    ]);
    expect(features[0].geometry).toEqual({
      type: "Point",
      coordinates: [-4.02, 5.34],
    });
  });

  it("keeps the query's row order, which is the intended reading order", () => {
    const { features } = toFeatures(source, [
      { latitude: 1, longitude: 1, name: "first" },
      { latitude: 2, longitude: 2, name: "second" },
    ]);
    expect(features.map((feature) => feature.properties.name)).toEqual([
      "first",
      "second",
    ]);
  });

  it("carries the other columns as properties for the popup", () => {
    const { features } = toFeatures(source, [
      { latitude: 5.34, longitude: -4.02, district: "Boundiali", cases: 12 },
    ]);
    expect(features[0].properties).toEqual({
      district: "Boundiali",
      cases: 12,
    });
  });

  it("leaves the coordinate columns out of the popup, which the marker already shows", () => {
    const { features } = toFeatures(source, [
      { latitude: 5.34, longitude: -4.02, name: "Diogo" },
    ]);
    expect(features[0].properties).not.toHaveProperty("latitude");
    expect(features[0].properties).not.toHaveProperty("longitude");
  });

  it("drops rows with no usable location instead of guessing at one", () => {
    const { features } = toFeatures(source, [
      { latitude: 5.34, longitude: -4.02 },
      { latitude: null, longitude: null },
      { latitude: "n/a", longitude: "n/a" },
    ]);
    expect(features).toHaveLength(1);
  });

  it("caps the features and reports how many were left off", () => {
    const rows = Array.from({ length: 5 }, () => ({
      latitude: 5.34,
      longitude: -4.02,
    }));
    expect(toFeatures(source, rows, 2)).toMatchObject({ hidden: 3 });
  });

  it("returns nothing for a geometry it cannot read", () => {
    expect(
      toFeatures({ kind: "unreadable-geometry", column: "geom" }, [
        { geom: WKB_POINT },
      ]),
    ).toEqual({ features: [], hidden: 0 });
  });
});
