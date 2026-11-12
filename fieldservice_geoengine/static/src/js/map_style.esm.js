/** @odoo-module **/

import {user} from "@web/core/user";

const MAP_ATTRIBUTION =
    '© <a href="https://openfreemap.org/">OpenFreeMap</a> ' +
    '© <a href="https://openmaptiles.org/">OpenMapTiles</a> ' +
    '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>';

const TILEJSON_URL = "https://tiles.openfreemap.org/planet";
const RELIEF_URL = "https://tiles.openfreemap.org/natural_earth/ne2sr/{z}/{x}/{y}.png";

let tileUrlPromise = null;

/**
 * User.lang is a JS locale (en-US), not the Odoo code (en_US).
 * OpenMapTiles stores that language as name_en, name_fr, name_th, ...
 */
export function mapLanguage() {
    return (user.lang || "en-US").split(/[_-]/)[0];
}

function featureLabel(feature) {
    const language = mapLanguage();
    return (
        feature.get(`name_${language}`) ||
        feature.get("name_en") ||
        feature.get("name:latin") ||
        feature.get("name") ||
        ""
    );
}

function zoomFromResolution(resolution) {
    return Math.log2(156543.03392804097 / resolution);
}

function textStyle(ol, text, size, placement) {
    return new ol.style.Text({
        text,
        font: `${size}px sans-serif`,
        placement: placement || "point",
        fill: new ol.style.Fill({color: "#1f2933"}),
        stroke: new ol.style.Stroke({color: "#ffffff", width: 3}),
        overflow: placement === "line",
    });
}

const fillCache = new Map();
const strokeCache = new Map();

function fillStyle(ol, color) {
    if (!fillCache.has(color)) {
        fillCache.set(color, new ol.style.Style({fill: new ol.style.Fill({color})}));
    }
    return fillCache.get(color);
}

function strokeStyle(ol, color, width) {
    const key = `${color}:${width}`;
    if (!strokeCache.has(key)) {
        strokeCache.set(
            key,
            new ol.style.Style({
                stroke: new ol.style.Stroke({color, width}),
            })
        );
    }
    return strokeCache.get(key);
}

function localizedStyle(ol, feature, resolution) {
    const layer = feature.get("layer");
    const zoom = zoomFromResolution(resolution);
    const kind = feature.get("class");
    if (layer === "water") {
        return fillStyle(ol, "#a4d4e8");
    }
    if (layer === "waterway" && zoom >= 10) {
        return strokeStyle(ol, "#a4d4e8", 1.5);
    }
    if (layer === "landcover" || layer === "park") {
        const green = ["grass", "wood", "forest", "farmland", "park"];
        if (layer === "park" || green.includes(kind)) {
            return fillStyle(ol, "#cde8c2");
        }
        return undefined;
    }
    if (layer === "landuse") {
        if (kind === "residential" && zoom >= 11) {
            return fillStyle(ol, "#f3efe6");
        }
        if (["park", "grass", "forest"].includes(kind)) {
            return fillStyle(ol, "#cde8c2");
        }
        return undefined;
    }
    if (layer === "building" && zoom >= 14) {
        return fillStyle(ol, "#e4ddd4");
    }
    if (layer === "transportation") {
        const roads = {
            motorway: ["#e892a2", 5, 6],
            trunk: ["#f9b29c", 4, 7],
            primary: ["#fcd6a4", 3.5, 9],
            secondary: ["#f7fabf", 3, 11],
            tertiary: ["#ffffff", 2.2, 12],
            minor: ["#ffffff", 1.4, 13],
            service: ["#ffffff", 1, 14],
        };
        const road = roads[kind];
        if (!road || zoom < road[2]) {
            return undefined;
        }
        return strokeStyle(ol, road[0], road[1]);
    }
    const labeled = [
        "place",
        "transportation_name",
        "water_name",
        "poi",
        "aerodrome_label",
    ];
    if (!labeled.includes(layer)) {
        return undefined;
    }
    if (layer === "poi" && zoom < 15) {
        return undefined;
    }
    if (layer === "transportation_name" && zoom < 14) {
        return undefined;
    }
    const label = featureLabel(feature);
    if (!label) {
        return undefined;
    }
    const alongLine = feature.getGeometry().getType().includes("Line");
    const size = kind === "city" ? 14 : layer === "place" ? 12 : 11;
    return new ol.style.Style({
        text: textStyle(ol, label, size, alongLine ? "line" : "point"),
    });
}

function vectorTileUrl() {
    if (!tileUrlPromise) {
        tileUrlPromise = fetch(TILEJSON_URL)
            .then((response) => response.json())
            .then((payload) => (payload.tiles || [])[0])
            .catch(() => "");
    }
    return tileUrlPromise;
}

/**
 * Basemap whose labels follow the Odoo user's language.
 * Raster tiles bake the local name into the image, so the streets come
 * from vector tiles and the label is name_<language>.
 */
export function localizedBaseLayers(ol) {
    const relief = new ol.layer.Tile({
        source: new ol.source.XYZ({
            url: RELIEF_URL,
            maxZoom: 6,
            attributions: MAP_ATTRIBUTION,
        }),
    });
    const source = new ol.source.VectorTile({
        format: new ol.format.MVT(),
        maxZoom: 14,
        attributions: MAP_ATTRIBUTION,
    });
    vectorTileUrl().then((url) => {
        if (url) {
            source.setUrl(url);
        }
    });
    const streets = new ol.layer.VectorTile({
        source,
        declutter: true,
        style: (feature, resolution) => localizedStyle(ol, feature, resolution),
    });
    return [relief, streets];
}

export function personIconSvg(color) {
    return `<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 36 36"><circle cx="18" cy="18" r="16" fill="${color}" stroke="#ffffff" stroke-width="2"/><circle cx="18" cy="13" r="4.5" fill="#ffffff"/><path d="M9 28.5c1.4-5.4 4.6-7.8 9-7.8s7.6 2.4 9 7.8" fill="#ffffff"/></svg>`;
}

export function personStyle(ol, color) {
    const svg = personIconSvg(color);
    return new ol.style.Style({
        image: new ol.style.Icon({
            src: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`,
            width: 36,
            height: 36,
            anchor: [0.5, 0.5],
        }),
    });
}

export function locationStyle(ol, color, text) {
    return new ol.style.Style({
        image: new ol.style.Circle({
            radius: text ? 11 : 8,
            fill: new ol.style.Fill({color}),
            stroke: new ol.style.Stroke({color: "#ffffff", width: 2}),
        }),
        text: text
            ? new ol.style.Text({
                  text: String(text),
                  fill: new ol.style.Fill({color: "#1f2933"}),
                  font: "bold 12px sans-serif",
              })
            : undefined,
    });
}

/**
 * Frame the map on the features currently drawn.
 * Retries until the map has a real size, so the first paint is not
 * stuck at the default world view.
 */
export function fitMapToExtent(map, extent, options) {
    if (!map || !extent || !extent.every((value) => Number.isFinite(value))) {
        return false;
    }
    map.updateSize();
    const size = map.getSize() || [0, 0];
    if (!size[0] || !size[1]) {
        return false;
    }
    map.getView().fit(extent, {
        maxZoom: 14,
        padding: [48, 48, 48, 48],
        duration: 0,
        ...(options || {}),
    });
    return true;
}

export function fitMapWhenReady(map, getExtent, options, attempt) {
    const extent = typeof getExtent === "function" ? getExtent() : getExtent;
    if (fitMapToExtent(map, extent, options)) {
        return;
    }
    if ((attempt || 0) < 8) {
        requestAnimationFrame(() =>
            fitMapWhenReady(map, getExtent, options, (attempt || 0) + 1)
        );
    }
}

export const LOCATION_COLOR = "#0AFF68";
export const WORKER_COLOR = "#1A56DB";
export const ROUTE_COLOR = "#1A56DB";
