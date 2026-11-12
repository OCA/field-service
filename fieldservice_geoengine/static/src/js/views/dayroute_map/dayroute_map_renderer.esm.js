/** @odoo-module **/

import {Component, onMounted, onWillStart, onWillUnmount, useEffect} from "@odoo/owl";
import {loadMapLibs} from "@base_geoengine/js/geoengine_libs.esm";

import {
    fitMapWhenReady,
    localizedBaseLayers,
    locationStyle,
    personStyle,
} from "../../map_style.esm";

const ROUTE_COLORS = ["#1A56DB", "#059669", "#D97706", "#E11D48", "#7C3AED", "#0891B2"];

let mapSeq = 0;

export class DayrouteMapRenderer extends Component {
    static template = "fieldservice_geoengine.DayrouteMapRenderer";
    static props = {
        list: Object,
        openDayroute: Function,
    };

    setup() {
        this.mapId = `dayroute_dashboard_${++mapSeq}`;
        onWillStart(async () => {
            this.ol = (await loadMapLibs()).ol;
        });
        onMounted(() => {
            this.renderMap();
            this.draw();
            const target = document.getElementById(this.mapId);
            this.resizeObserver = new ResizeObserver(() => {
                if (this.map) {
                    this.map.updateSize();
                }
            });
            if (target) {
                this.resizeObserver.observe(target);
            }
        });
        onWillUnmount(() => {
            if (this.resizeObserver) {
                this.resizeObserver.disconnect();
            }
        });
        useEffect(
            () => {
                this.draw();
            },
            () => [this.signature()]
        );
    }

    get routes() {
        return (this.props.list.records || []).map((record, index) => ({
            id: record.resId,
            name: record.data.name,
            color: ROUTE_COLORS[index % ROUTE_COLORS.length],
        }));
    }

    signature() {
        return (this.props.list.records || [])
            .map(
                (record) =>
                    `${record.resId}:${JSON.stringify(record.data.map_payload || {})}`
            )
            .join("|");
    }

    renderMap() {
        const ol = this.ol;
        this.source = new ol.source.Vector();
        this.map = new ol.Map({
            target: this.mapId,
            layers: [
                ...localizedBaseLayers(ol),
                new ol.layer.Vector({
                    source: this.source,
                    style: (feature) => feature.get("markerStyle"),
                }),
            ],
            view: new ol.View({center: [0, 0], zoom: 2}),
        });
        this.map.on("click", (event) => {
            const feature = this.map.forEachFeatureAtPixel(event.pixel, (item) => item);
            const resId = feature && feature.get("resId");
            if (resId) {
                this.props.openDayroute(resId);
            }
        });
    }

    draw() {
        if (!this.map) {
            return;
        }
        this.source.clear();
        (this.props.list.records || []).forEach((record, index) => {
            this.drawRoute(record, ROUTE_COLORS[index % ROUTE_COLORS.length]);
        });
        this.fit();
    }

    drawRoute(record, color) {
        const ol = this.ol;
        const payload = record.data.map_payload || {};
        const stops = payload.stops || [];
        const routePoints = [];
        const worker = payload.worker;
        if (worker && (worker.lat || worker.lon)) {
            const coordinate = ol.proj.fromLonLat([worker.lon, worker.lat]);
            routePoints.push(coordinate);
            const feature = new ol.Feature({
                geometry: new ol.geom.Point(coordinate),
            });
            feature.set("resId", record.resId);
            feature.set("markerStyle", personStyle(ol, color));
            this.source.addFeature(feature);
        }
        stops.forEach((stop) => {
            if (!stop.lat && !stop.lon) {
                return;
            }
            const coordinate = ol.proj.fromLonLat([stop.lon, stop.lat]);
            if (stop.step) {
                routePoints.push(coordinate);
            }
            const feature = new ol.Feature({
                geometry: new ol.geom.Point(coordinate),
            });
            feature.set("resId", record.resId);
            feature.set(
                "markerStyle",
                locationStyle(ol, color, stop.step || undefined)
            );
            this.source.addFeature(feature);
        });
        const path = payload.path || [];
        const line =
            path.length > 1
                ? path.map((coord) => ol.proj.fromLonLat(coord))
                : routePoints;
        if (line.length > 1) {
            const feature = new ol.Feature({
                geometry: new ol.geom.LineString(line),
            });
            feature.set("resId", record.resId);
            feature.set(
                "markerStyle",
                new ol.style.Style({
                    stroke: new ol.style.Stroke({color, width: 4}),
                })
            );
            this.source.addFeature(feature);
        }
    }

    fit() {
        fitMapWhenReady(this.map, () => this.source.getExtent(), {
            maxZoom: 14,
            padding: [48, 48, 80, 48],
        });
    }
}
