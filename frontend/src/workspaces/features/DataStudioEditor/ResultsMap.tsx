import "maplibre-gl/dist/maplibre-gl.css";

import type { FeatureCollection } from "geojson";
import type {
  GeoJSONSource,
  LayerSpecification,
  Map as MaplibreMap,
  StyleSpecification,
} from "maplibre-gl";
import { setWorkerUrl } from "maplibre-gl";
import { useTranslation } from "next-i18next";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type {
  MapEvent,
  MapLayerMouseEvent,
  MapRef,
  ViewStateChangeEvent,
} from "react-map-gl/maplibre";
import Map, { NavigationControl, Popup } from "react-map-gl/maplibre";
import { stringifyCellValue } from "./format";
import { featuresBounds, MapBounds, MapFeature } from "./map";

type ResultsMapProps = {
  features: MapFeature[];
};

/**
 * MapLibre tiles GeoJSON inside a Web Worker, which it loads as a separate ES
 * module. It finds that module by resolving `import.meta.url`, and inside a Next
 * bundle that is not an http URL, so the lookup returns an empty string and no
 * worker ever runs: the basemap renders and the data is silently absent, with no
 * error raised. Pointing `setWorkerUrl` at a copy we serve ourselves is
 * MapLibre's documented answer for bundlers, and Next needs it in both the
 * Turbopack and webpack modes.
 *
 * `frontend/scripts/copy-maplibre-worker.mjs` puts the files under
 * `public/maplibre/` before every dev and build. The base path is prepended
 * because a deployment can be served from a sub-path, where a root-relative
 * worker URL would 404 — and a 404 here costs the whole map's data.
 *
 * Called at module scope so it runs before <Map> can construct anything. The
 * module itself is only loaded once a map is actually shown, since
 * DataStudioResults imports it dynamically.
 */
setWorkerUrl(
  `${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/maplibre/maplibre-gl-worker.mjs`,
);

// OpenStreetMap's public tiles: no API key and no account, and a deployment that
// cannot reach them can point this one style at its own mirror. MapLibre needs a
// style document rather than a URL template, so the raster source is declared
// here; `attribution` is required by OSM's terms and MapLibre renders it into
// the map's own attribution control.
const BASEMAP_STYLE: StyleSpecification = {
  version: 8,
  sources: {
    osm: {
      type: "raster",
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      maxzoom: 19,
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    },
  },
  layers: [{ id: "osm", type: "raster", source: "osm" }],
};

const SOURCE_ID = "results";

const POINT_COLOR = "#3b82f6";
const STROKE_COLOR = "#2563eb";

// One source holds every geometry type a query can return, so each layer selects
// its own with a filter: MapLibre applies a paint style per layer, not per
// feature. Points are drawn as flat circles rather than pins — a pin needs a
// sprite image, and a circle reads better when hundreds of points overlap, which
// is the normal case for survey data.
//
// Array order is paint order, and also hit-test order: the layer added last is
// picked first, so a point inside a polygon opens the point's popup.
const LAYERS: LayerSpecification[] = [
  {
    id: "results-fill",
    type: "fill",
    source: SOURCE_ID,
    filter: [
      "match",
      ["geometry-type"],
      ["Polygon", "MultiPolygon"],
      true,
      false,
    ],
    paint: { "fill-color": POINT_COLOR, "fill-opacity": 0.2 },
  },
  // Draws polygon borders as well as line features: `fill` has no width of its
  // own, so an outline needs a line layer over the same geometries.
  {
    id: "results-line",
    type: "line",
    source: SOURCE_ID,
    filter: [
      "match",
      ["geometry-type"],
      ["Polygon", "MultiPolygon", "LineString", "MultiLineString"],
      true,
      false,
    ],
    paint: { "line-color": STROKE_COLOR, "line-width": 2 },
  },
  {
    id: "results-point",
    type: "circle",
    source: SOURCE_ID,
    filter: ["match", ["geometry-type"], ["Point", "MultiPoint"], true, false],
    paint: {
      "circle-radius": 5,
      "circle-color": POINT_COLOR,
      "circle-opacity": 0.6,
      "circle-stroke-color": STROKE_COLOR,
      "circle-stroke-width": 1,
    },
  },
];

const INTERACTIVE_LAYER_IDS = LAYERS.map((layer) => layer.id);

// Used when the features carry no usable extent, which a valid GeoJSON geometry
// with an empty coordinate array can produce. Longitude first, as MapLibre and
// GeoJSON both order it — the reverse of Leaflet's lat/lon pairs.
const WORLD_BOUNDS: MapBounds = [
  [-180, -60],
  [180, 75],
];

const FIT_OPTIONS = { padding: 24, maxZoom: 14 } as const;

// Only a row index travels through the map: feature properties go through
// MapLibre's tiler, so reading a popup's values back off the map risks showing
// something subtly different from the table tab. The values are read from the
// rows we were handed instead, and the popup holds the row itself rather than the
// index, so it cannot end up pointing into a later result.
const FEATURE_INDEX = "_index";

type Selection = {
  longitude: number;
  latitude: number;
  properties: MapFeature["properties"];
};

const ResultsMap = ({ features }: ResultsMapProps) => {
  const { t } = useTranslation();
  const mapRef = useRef<MapRef>(null);
  const [selection, setSelection] = useState<Selection | null>(null);
  const [hovering, setHovering] = useState(false);

  const data = useMemo<FeatureCollection>(
    () => ({
      type: "FeatureCollection",
      features: features.map((feature, index) => ({
        type: "Feature",
        geometry: feature.geometry,
        properties: { [FEATURE_INDEX]: index },
      })),
    }),
    [features],
  );

  const bounds = useMemo(
    () => featuresBounds(features) ?? WORLD_BOUNDS,
    [features],
  );

  // Read inside callbacks that must not be rebuilt when the data changes: the
  // map's own handlers are registered once, and a stale closure would frame or
  // publish the previous result.
  const dataRef = useRef(data);
  dataRef.current = data;
  const boundsRef = useRef(bounds);
  boundsRef.current = bounds;

  const frame = useCallback((map: MaplibreMap) => {
    map.fitBounds(boundsRef.current, { ...FIT_OPTIONS, duration: 0 });
  }, []);

  /**
   * The source and the layers are installed by hand rather than declared as
   * <Source>/<Layer> children. Those components decide whether the map is ready
   * by reading its private `style._loaded` flag, and when it reads false they
   * render nothing at all — children included — so a missed window leaves the
   * layers absent from the style with no error raised. The load event is
   * MapLibre's own documented signal that the style is ready, and it is one call
   * each from there.
   */
  const install = useCallback((map: MaplibreMap) => {
    if (!map.getSource(SOURCE_ID)) {
      map.addSource(SOURCE_ID, { type: "geojson", data: dataRef.current });
    }
    for (const layer of LAYERS) {
      if (!map.getLayer(layer.id)) {
        map.addLayer(layer);
      }
    }
  }, []);

  // Every later result reaches the map through the source it already holds:
  // re-adding the layers on each query would drop their paint state and the
  // camera along with it.
  useEffect(() => {
    const source = mapRef.current?.getMap().getSource(SOURCE_ID);
    (source as GeoJSONSource | undefined)?.setData(data);
  }, [data]);

  // Framing the data rather than holding a fixed centre and zoom: a result is
  // only useful if its rows are on screen, and successive queries land on
  // different continents.
  //
  // Keyed on the extent's values, not on the array holding them: the features
  // are rebuilt on every parent render, so framing on identity would haul the
  // map back to the data whenever an unrelated piece of state changed, undoing
  // whatever the user had panned to. The open popup goes with a genuine change,
  // since the row it is showing is no longer in the result.
  const boundsKey = String(bounds);

  // The map is created inside a panel the user can drag, and it can be measured
  // at zero height before that panel settles — a fit computed against a zero-size
  // viewport leaves the camera nowhere near the data. Framing again on every
  // resize covers that, but only until the user takes over: once they have
  // panned or zoomed themselves, dragging the panel must leave their view alone.
  // A new result resets that, since it is being framed from scratch anyway.
  const userMoved = useRef(false);

  useEffect(() => {
    setSelection(null);
    userMoved.current = false;
    const map = mapRef.current?.getMap();
    if (map) {
      frame(map);
    }
  }, [boundsKey, frame]);

  const handleLoad = useCallback(
    (event: MapEvent) => {
      install(event.target);
      // react-map-gl publishes the map ref a render after mounting, so the
      // effects above find it empty on the first pass; the load event carries
      // the map directly, and fires once the container has its real size.
      frame(event.target);
    },
    [install, frame],
  );

  const handleMoveStart = useCallback((event: ViewStateChangeEvent) => {
    // Present for a gesture, absent for the programmatic fits.
    if (event.originalEvent) {
      userMoved.current = true;
    }
  }, []);

  const handleResize = useCallback(
    (event: MapEvent) => {
      if (!userMoved.current) {
        frame(event.target);
      }
    },
    [frame],
  );

  const handleClick = useCallback(
    (event: MapLayerMouseEvent) => {
      const index = event.features?.[0]?.properties?.[FEATURE_INDEX];
      const feature = typeof index === "number" ? features[index] : undefined;
      if (!feature) {
        return;
      }
      setSelection({
        longitude: event.lngLat.lng,
        latitude: event.lngLat.lat,
        properties: feature.properties,
      });
    },
    [features],
  );

  const handleMouseMove = useCallback((event: MapLayerMouseEvent) => {
    setHovering((event.features?.length ?? 0) > 0);
  }, []);

  if (features.length === 0) {
    return (
      <div className="flex h-full items-center justify-center px-6 text-center text-sm text-gray-400">
        {t("No row in this result has a location that can be mapped.")}
      </div>
    );
  }

  return (
    <Map
      ref={mapRef}
      mapStyle={BASEMAP_STYLE}
      initialViewState={{ bounds, fitBoundsOptions: FIT_OPTIONS }}
      style={{ height: "100%", width: "100%" }}
      interactiveLayerIds={INTERACTIVE_LAYER_IDS}
      onLoad={handleLoad}
      onResize={handleResize}
      onMoveStart={handleMoveStart}
      onClick={handleClick}
      onMouseMove={handleMouseMove}
      cursor={hovering ? "pointer" : "grab"}
    >
      <NavigationControl position="top-left" showCompass={false} />
      {selection && (
        <Popup
          longitude={selection.longitude}
          latitude={selection.latitude}
          onClose={() => setSelection(null)}
          closeOnClick={false}
          maxWidth="320px"
        >
          {/* Rendered as React nodes, so a cell holding markup shows as text
              without anything having to escape it by hand. */}
          <dl className="grid max-h-60 grid-cols-[auto_1fr] gap-x-3 gap-y-0.5 overflow-auto text-xs">
            {Object.entries(selection.properties).map(([key, value]) => (
              <div key={key} className="col-span-2 grid grid-cols-subgrid">
                <dt className="font-medium text-gray-500">{key}</dt>
                <dd className="font-mono text-gray-900">
                  {stringifyCellValue(value)}
                </dd>
              </div>
            ))}
          </dl>
        </Popup>
      )}
    </Map>
  );
};

export default ResultsMap;
