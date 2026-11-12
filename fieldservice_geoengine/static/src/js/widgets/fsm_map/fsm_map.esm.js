/** @odoo-module **/

import {Component, onMounted, onWillStart, onWillUnmount, useEffect} from "@odoo/owl";
import {loadMapLibs} from "@base_geoengine/js/geoengine_libs.esm";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useService} from "@web/core/utils/hooks";

import {
    LOCATION_COLOR,
    ROUTE_COLOR,
    WORKER_COLOR,
    fitMapWhenReady,
    localizedBaseLayers,
    locationStyle,
    personStyle,
} from "../../map_style.esm";

let mapSeq = 0;

class FsmMap extends Component {
    setup() {
        this.mapId = `fsm_map_${++mapSeq}`;
        this.orm = useService("orm");
        this.ol = null;
        onWillStart(async () => {
            this.ol = (await loadMapLibs()).ol;
            if (this.geoColumn) {
                const info = await this.orm.call(
                    this.props.record.resModel,
                    "get_edit_info_for_geo_column",
                    [this.geoColumn]
                );
                this.srid = info.srid;
                this.defaultExtent = info.default_extent;
                this.defaultZoom = info.default_zoom;
            }
        });
        onMounted(() => {
            this.renderMap();
            this.redraw();
            const target = document.getElementById(this.mapId);
            this.resizeObserver = new ResizeObserver(() => {
                if (!this.map) {
                    return;
                }
                const size = this.map.getSize();
                this.map.updateSize();
                const next = this.map.getSize();
                if (next && next[0] > 0 && (!size || size[0] === 0)) {
                    this.fit();
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
                this.redraw();
            },
            () => [this.signature()]
        );
    }

    get geoColumn() {
        return this.props.name;
    }

    signature() {
        return "";
    }

    renderMap() {
        const ol = this.ol;
        this.source = new ol.source.Vector();
        this.vectorLayer = new ol.layer.Vector({
            source: this.source,
            style: (feature) => feature.get("markerStyle") || this.lineStyle(),
        });
        this.map = new ol.Map({
            target: this.mapId,
            layers: [...localizedBaseLayers(ol), this.vectorLayer],
            view: new ol.View({center: [0, 0], zoom: 2}),
        });
        this.format = new ol.format.GeoJSON({
            featureProjection: this.map.getView().getProjection(),
            dataProjection: `EPSG:${this.srid || 3857}`,
        });
    }

    lineStyle() {
        return new this.ol.style.Style({
            stroke: new this.ol.style.Stroke({
                color: ROUTE_COLOR,
                width: 3,
            }),
        });
    }

    redraw() {
        if (!this.map) {
            return;
        }
        this.source.clear();
        this.drawFeatures();
        this.fit();
    }

    drawFeatures() {}

    addGeoPoint(geojson, style) {
        if (!geojson) {
            return;
        }
        const geometry = this.format.readGeometry(geojson);
        const feature = new this.ol.Feature({geometry});
        feature.set("markerStyle", style);
        this.source.addFeature(feature);
    }

    addLonLat(lon, lat, style) {
        if (!lat && !lon) {
            return;
        }
        const feature = new this.ol.Feature({
            geometry: new this.ol.geom.Point(
                this.ol.proj.fromLonLat([lon, lat])
            ),
        });
        feature.set("markerStyle", style);
        this.source.addFeature(feature);
    }

    fit() {
        const extent = this.source.getExtent();
        if (extent && extent.every((value) => Number.isFinite(value))) {
            fitMapWhenReady(this.map, extent, {
                maxZoom: this.defaultZoom || 16,
                padding: [80, 80, 80, 80],
            });
            return;
        }
        if (this.defaultExtent) {
            const box = this.defaultExtent
                .replace(/\s/g, "")
                .split(",")
                .map((coord) => Number(coord));
            fitMapWhenReady(this.map, box, {maxZoom: this.defaultZoom || 5});
        }
    }
}

export class FsmOrderMap extends FsmMap {
    static template = "fieldservice_geoengine.FsmOrderMap";
    static props = {...standardFieldProps};

    signature() {
        const data = this.props.record.data;
        return `${data.shape || ""}|${data.worker_shape || ""}`;
    }

    drawFeatures() {
        const ol = this.ol;
        const data = this.props.record.data;
        this.addGeoPoint(data.shape, locationStyle(ol, LOCATION_COLOR));
        this.addGeoPoint(data.worker_shape, personStyle(ol, WORKER_COLOR));
    }
}

export class FsmRouteMap extends FsmMap {
    static template = "fieldservice_geoengine.FsmRouteMap";
    static props = {...standardFieldProps};

    get geoColumn() {
        return null;
    }

    signature() {
        return JSON.stringify(this.props.record.data.map_payload || {});
    }

    drawFeatures() {
        const ol = this.ol;
        const payload = this.props.record.data.map_payload || {};
        const stops = payload.stops || [];
        const routePoints = [];
        const worker = payload.worker;
        if (worker && (worker.lat || worker.lon)) {
            routePoints.push(ol.proj.fromLonLat([worker.lon, worker.lat]));
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
            feature.set(
                "markerStyle",
                locationStyle(ol, LOCATION_COLOR, stop.step || undefined)
            );
            this.source.addFeature(feature);
        });
        const path = payload.path || [];
        const line =
            path.length > 1
                ? path.map((coord) => ol.proj.fromLonLat(coord))
                : routePoints;
        if (line.length > 1) {
            this.source.addFeature(
                new ol.Feature({
                    geometry: new ol.geom.LineString(line),
                })
            );
        }
        if (worker) {
            this.addLonLat(worker.lon, worker.lat, personStyle(ol, WORKER_COLOR));
        }
    }
}

export class FsmLocationMap extends FsmMap {
    static template = "fieldservice_geoengine.FsmLocationMap";
    static props = {...standardFieldProps};

    get geoColumn() {
        return "area_shape";
    }

    get isArea() {
        return this.props.record.data.shape_kind === "area";
    }

    signature() {
        const data = this.props.record.data;
        return `${data.shape_kind || ""}|${data.shape || ""}|${data.area_shape || ""}`;
    }

    drawFeatures() {
        this.clearDraw();
        if (this.isArea) {
            if (this.props.record.data.area_shape) {
                this.addGeoPoint(
                    this.props.record.data.area_shape,
                    new this.ol.style.Style({
                        fill: new this.ol.style.Fill({
                            color: "rgba(10, 255, 104, 0.35)",
                        }),
                        stroke: new this.ol.style.Stroke({
                            color: LOCATION_COLOR,
                            width: 2,
                        }),
                    })
                );
            } else {
                // Keep the address in view so the area is drawn around it.
                this.addGeoPoint(
                    this.props.record.data.shape,
                    locationStyle(this.ol, LOCATION_COLOR)
                );
            }
            if (!this.props.readonly) {
                this.setupAreaControls();
            }
            return;
        }
        this.addGeoPoint(
            this.props.record.data.shape,
            locationStyle(this.ol, LOCATION_COLOR)
        );
    }

    clearDraw() {
        if (this.drawInteraction) {
            this.map.removeInteraction(this.drawInteraction);
            this.drawInteraction = undefined;
        }
        if (this.modifyInteraction) {
            this.map.removeInteraction(this.modifyInteraction);
            this.modifyInteraction = undefined;
        }
        if (this.trashControl) {
            this.map.removeControl(this.trashControl);
            this.trashControl = undefined;
        }
    }

    setupAreaControls() {
        const ol = this.ol;
        const hasArea = Boolean(this.props.record.data.area_shape);
        if (!hasArea) {
            this.drawInteraction = new ol.interaction.Draw({
                type: "Polygon",
                source: this.source,
            });
            this.map.addInteraction(this.drawInteraction);
            this.drawInteraction.on("drawend", (event) => {
                this.onAreaChange(event.feature.getGeometry());
            });
        } else {
            this.modifyInteraction = new ol.interaction.Modify({
                source: this.source,
            });
            this.map.addInteraction(this.modifyInteraction);
            this.modifyInteraction.on("modifyend", (event) => {
                event.features.forEach((feature) => {
                    this.onAreaChange(feature.getGeometry());
                });
            });
        }
        const button = document.createElement("button");
        button.innerHTML = '<i class="fa fa-trash"/>';
        button.type = "button";
        button.addEventListener("click", () => {
            this.source.clear();
            this.onAreaChange(null);
        });
        const element = document.createElement("div");
        element.className = "ol-clear ol-unselectable ol-control";
        element.appendChild(button);
        this.trashControl = new ol.control.Control({element});
        this.map.addControl(this.trashControl);
    }

    onAreaChange(geometry) {
        const value = geometry ? this.format.writeGeometry(geometry) : false;
        this.props.record.update({[this.props.name]: value});
    }
}

export class FsmRouteAreaMap extends FsmLocationMap {
    static template = "fieldservice_geoengine.FsmRouteAreaMap";
    static props = {...standardFieldProps};

    get geoColumn() {
        return "area_shape";
    }

    setup() {
        this.locations = [];
        super.setup();
        onWillStart(async () => {
            this.locations = await this.orm.searchRead(
                "fsm.location",
                ["|", ["partner_latitude", "!=", 0], ["partner_longitude", "!=", 0]],
                ["name", "shape"]
            );
        });
    }

    signature() {
        return this.props.record.data.area_shape || "";
    }

    renderMap() {
        super.renderMap();
        const ol = this.ol;
        this.locationSource = new ol.source.Vector();
        this.map.addLayer(
            new ol.layer.Vector({
                source: this.locationSource,
                style: locationStyle(ol, LOCATION_COLOR),
            })
        );
    }

    drawFeatures() {
        this.clearDraw();
        const ol = this.ol;
        this.locationSource.clear();
        (this.locations || []).forEach((location) => {
            if (!location.shape) {
                return;
            }
            this.locationSource.addFeature(
                new ol.Feature({geometry: this.format.readGeometry(location.shape)})
            );
        });
        if (this.props.record.data.area_shape) {
            this.addGeoPoint(
                this.props.record.data.area_shape,
                new ol.style.Style({
                    fill: new ol.style.Fill({color: "rgba(26, 86, 219, 0.25)"}),
                    stroke: new ol.style.Stroke({color: ROUTE_COLOR, width: 2}),
                })
            );
        }
        if (!this.props.readonly) {
            this.setupAreaControls();
        }
    }

    fit() {
        const ol = this.ol;
        const extent = ol.extent.createEmpty();
        ol.extent.extend(extent, this.source.getExtent());
        ol.extent.extend(extent, this.locationSource.getExtent());
        if (!ol.extent.isEmpty(extent)) {
            fitMapWhenReady(this.map, extent, {
                maxZoom: this.defaultZoom || 14,
                padding: [80, 80, 80, 80],
            });
            return;
        }
        super.fit();
    }
}

export class FsmHiddenGeo extends Component {
    static template = "fieldservice_geoengine.FsmHiddenGeo";
    static props = {...standardFieldProps};
}

registry.category("fields").add("fsm_order_map", {component: FsmOrderMap});
registry.category("fields").add("fsm_route_map", {component: FsmRouteMap});
registry.category("fields").add("fsm_location_map", {component: FsmLocationMap});
registry.category("fields").add("fsm_route_area_map", {component: FsmRouteAreaMap});
registry.category("fields").add("fsm_hidden_geo", {component: FsmHiddenGeo});
