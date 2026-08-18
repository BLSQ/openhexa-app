import "leaflet/dist/leaflet.css";

import type { Feature, FeatureCollection } from "geojson";
import {
  CircleMarker,
  geoJSON,
  type CircleMarkerOptions,
  type LatLngBoundsExpression,
  type Layer,
  type PathOptions,
} from "leaflet";
import { useTranslation } from "next-i18next";
import { useEffect, useMemo, useRef } from "react";
import { GeoJSON, MapContainer, TileLayer, useMap } from "react-leaflet";
import { stringifyCellValue } from "./format";
import { MapFeature } from "./map";

type ResultsMapProps = {
  features: MapFeature[];
};

// OpenStreetMap's public tiles: no API key and no account, and a deployment
// that cannot reach them can point this one URL at its own mirror. Attribution
// is required by their terms and is rendered by the TileLayer itself.
const TILE_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const TILE_ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

// Circle markers rather than Leaflet's default pin: the pin ships as an image
// whose URL breaks under bundlers, and a flat circle reads better when hundreds
// of points overlap, which is the normal case for survey data.
const POINT_STYLE: CircleMarkerOptions = {
  radius: 5,
  color: "#2563eb",
  weight: 1,
  fillColor: "#3b82f6",
  fillOpacity: 0.6,
};

const SHAPE_STYLE: PathOptions = {
  color: "#2563eb",
  weight: 2,
  fillColor: "#3b82f6",
  fillOpacity: 0.2,
};

// Used when the features carry no usable extent — every point at the same spot
// yields a zero-area bounds Leaflet cannot fit to.
const WORLD_BOUNDS: LatLngBoundsExpression = [
  [-60, -180],
  [75, 180],
];

const escapeHtml = (value: string) =>
  value.replace(
    /[&<>"]/g,
    (character) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[character]!,
  );

/**
 * Popups are built as an HTML string because Leaflet renders them itself rather
 * than through React. Every value is escaped: it comes from the database, and a
 * cell holding markup must show as text, never render as it.
 */
const bindPopup = (feature: Feature, layer: Layer) => {
  const entries = Object.entries(feature.properties ?? {});
  if (entries.length === 0) {
    return;
  }
  layer.bindPopup(
    `<dl class="grid grid-cols-[auto_1fr] gap-x-3 gap-y-0.5 text-xs">${entries
      .map(
        ([key, value]) =>
          `<dt class="font-medium text-gray-500">${escapeHtml(key)}</dt>` +
          `<dd class="font-mono text-gray-900">${escapeHtml(
            stringifyCellValue(value),
          )}</dd>`,
      )
      .join("")}</dl>`,
    { maxHeight: 240 },
  );
};

/**
 * Frames the data rather than holding a fixed centre and zoom: a result is only
 * useful if its rows are on screen, and successive queries land on different
 * continents. Lives inside MapContainer because `useMap` only exposes the map
 * instance to its children.
 */
const FitToFeatures = ({ data }: { data: FeatureCollection }) => {
  const map = useMap();

  useEffect(() => {
    if (data.features.length === 0) {
      map.fitBounds(WORLD_BOUNDS);
      return;
    }
    // The extent is computed from a throwaway layer: cheaper than walking every
    // geometry type by hand, and correct for lines and polygons too.
    const bounds = geoJSON(data).getBounds();
    map.fitBounds(bounds.isValid() ? bounds : WORLD_BOUNDS, {
      padding: [24, 24],
      maxZoom: 14,
    });
  }, [data, map]);

  return null;
};

const ResultsMap = ({ features }: ResultsMapProps) => {
  const { t } = useTranslation();

  const data = useMemo<FeatureCollection>(
    () => ({
      type: "FeatureCollection",
      features: features.map((feature) => ({
        type: "Feature",
        geometry: feature.geometry,
        properties: feature.properties,
      })),
    }),
    [features],
  );

  // react-leaflet's GeoJSON layer reads `data` once, when it mounts, so a new
  // result has to remount it. Counting the changes gives a key that moves
  // exactly when the data does — comparing during render rather than in an
  // effect so the layer never renders one result behind.
  const revision = useRef(0);
  const rendered = useRef(data);
  if (rendered.current !== data) {
    rendered.current = data;
    revision.current += 1;
  }

  if (features.length === 0) {
    return (
      <div className="flex h-full items-center justify-center px-6 text-center text-sm text-gray-400">
        {t("No row in this result has a location that can be mapped.")}
      </div>
    );
  }

  return (
    <MapContainer className="h-full w-full" center={[0, 0]} zoom={2}>
      <TileLayer url={TILE_URL} attribution={TILE_ATTRIBUTION} />
      <GeoJSON
        key={revision.current}
        data={data}
        style={SHAPE_STYLE}
        pointToLayer={(_feature, latlng) =>
          new CircleMarker(latlng, POINT_STYLE)
        }
        onEachFeature={bindPopup}
      />
      <FitToFeatures data={data} />
    </MapContainer>
  );
};

export default ResultsMap;
