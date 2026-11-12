/**
 * Copyright 2024 APSL-Nagarro
 */

/* global chroma, geostats, ol */

import {GeoengineRenderer} from "@base_geoengine/js/views/geoengine/geoengine_renderer/geoengine_renderer.esm";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";
import {sprintf} from "@web/core/utils/strings";

import {
    fitMapWhenReady,
    localizedBaseLayers,
    personIconSvg,
} from "@fieldservice_geoengine/js/map_style.esm";

/* CONSTANTS */
const DEFAULT_BEGIN_COLOR = "#FFFFFF";
const DEFAULT_END_COLOR = "#000000";
const LEGEND_MAX_ITEMS = 10;
const DEFAULT_NUM_CLASSES = 5;

patch(GeoengineRenderer.prototype, {
    updateZoom() {
        const view = this.map && this.map.getView();
        if (!view) {
            return;
        }
        const records = (this.props.data && this.props.data.records) || [];
        const key = records
            .map((record) => record.resId)
            .sort()
            .join(",");
        const extent = this._visibleRecordExtent();
        if (extent) {
            if (key === this._fittedRecordKey) {
                return;
            }
            this._fittedRecordKey = key;
            fitMapWhenReady(this.map, extent, {
                padding: [48, 240, 48, 200],
            });
            this.state.isFit = true;
            return;
        }
        if (!view.getCenter()) {
            view.setCenter(ol.proj.fromLonLat([0, 15]));
            view.setZoom(2);
        }
    },
    _visibleRecordExtent() {
        const extent = ol.extent.createEmpty();
        for (const layer of this.vectorLayersResult || []) {
            if (layer.getVisible && !layer.getVisible()) {
                continue;
            }
            const source = layer.getSource && layer.getSource();
            const layerExtent = source && source.getExtent && source.getExtent();
            if (
                layerExtent &&
                layerExtent.every((value) => Number.isFinite(value))
            ) {
                ol.extent.extend(extent, layerExtent);
            }
        }
        return ol.extent.isEmpty(extent) ? null : extent;
    },
    createBackgroundLayers(backgrounds) {
        const layers = super.createBackgroundLayers(backgrounds);
        const rest = layers.filter(
            (layer) =>
                !(layer.getSource && layer.getSource() instanceof ol.source.OSM)
        );
        if (rest.length === layers.length) {
            return layers;
        }
        return [...localizedBaseLayers(ol), ...rest];
    },
    hidePopup() {
        super.hidePopup(...arguments);
        this._clearOrderPath();
    },
    updateInfoBox(features) {
        super.updateInfoBox(...arguments);
        const feature = features && features.item(0);
        this._showOrderPath(feature && feature.getId());
    },
    onDisplayPopupRecord(record) {
        super.onDisplayPopupRecord(...arguments);
        this._showOrderPath(record && record.resId);
    },
    _clearOrderPath() {
        this._pathToken = (this._pathToken || 0) + 1;
        if (this.orderPathSource) {
            this.orderPathSource.clear();
        }
    },
    _ensureOrderPathLayer() {
        if (this.orderPathSource || !this.map) {
            return;
        }
        this.orderPathSource = new ol.source.Vector();
        this.map.addLayer(
            new ol.layer.Vector({
                title: "Order path",
                source: this.orderPathSource,
                style: new ol.style.Style({
                    stroke: new ol.style.Stroke({color: "#1A56DB", width: 4}),
                }),
                zIndex: 40,
            })
        );
    },
    async _showOrderPath(resId) {
        this._ensureOrderPathLayer();
        if (!this.orderPathSource) {
            return;
        }
        const token = (this._pathToken = (this._pathToken || 0) + 1);
        this.orderPathSource.clear();
        if (this.props.data.resModel !== "fsm.order" || !resId) {
            return;
        }
        const record = (this.props.data.records || []).find(
            (item) => item.resId === resId
        );
        let path = [];
        try {
            path = (await this.orm.call("fsm.order", "get_worker_path", [[resId]])) || [];
        } catch (error) {
            path = [];
        }
        if (token !== this._pathToken || !this.orderPathSource) {
            return;
        }
        const line =
            path.length > 1
                ? path.map((coord) => ol.proj.fromLonLat(coord))
                : [record && record.data.worker_shape, record && record.data.shape]
                      .filter(Boolean)
                      .map((geojson) => {
                          const geometry = new ol.format.GeoJSON().readGeometry(geojson);
                          return geometry.getCoordinates();
                      });
        if (line.length > 1) {
            this.orderPathSource.addFeature(
                new ol.Feature({geometry: new ol.geom.LineString(line)})
            );
        }
    },
    selectStyle(feature) {
        const geometry = feature.getGeometry();
        const type = geometry && geometry.getType();
        if (type === "Polygon") {
            return new ol.style.Style({
                fill: new ol.style.Fill({color: "rgba(0, 153, 255, 0.35)"}),
                stroke: new ol.style.Stroke({color: "#ffffff", width: 2}),
                zIndex: Infinity,
            });
        }
        return super.selectStyle(...arguments);
    },
    /**
     * A location is either a point or a drawn area. Each vector layer
     * plots only the geometry that matches the current choice.
     */
    _locationLayerMatches(vector, record) {
        if (this.props.data.resModel !== "fsm.location") {
            return true;
        }
        const geoField = vector.geo_field_id && vector.geo_field_id[1];
        const kind = record.data.shape_kind || "point";
        if (geoField === "area_shape") {
            return kind === "area";
        }
        if (geoField === "shape") {
            return kind !== "area";
        }
        return true;
    },
    styleVectorLayerColored(cfg, data) {
        const geoField = cfg.geo_field_id && cfg.geo_field_id[1];
        this._markerKind =
            geoField === "worker_shape" || this.props.data.resModel === "fsm.person"
                ? "worker"
                : "location";
        var indicator = cfg.attribute_field_id[1];
        var values = this.extractLayerValues(cfg, data);
        var nb_class = cfg.nb_class || DEFAULT_NUM_CLASSES;
        var opacity = cfg.layer_opacity;
        var begin_color_hex = cfg.begin_color || DEFAULT_BEGIN_COLOR;
        var end_color_hex = cfg.end_color || DEFAULT_END_COLOR;
        var begin_color = chroma(begin_color_hex).alpha(opacity).css();
        var end_color = chroma(end_color_hex).alpha(opacity).css();
        // Function that maps numeric values to a color palette.
        // This scale function is only used when geo_repr is basic
        var scale = chroma.scale([begin_color, end_color]);
        var serie = new geostats(values);
        var vals = null;
        switch (cfg.classification) {
            case "unique":
            case "custom":
                vals = serie.getClassUniqueValues();
                if (
                    cfg.classification === "custom" &&
                    vals.some((item) => item === 0 || typeof item === "string")
                ) {
                    this.notification.add(
                        sprintf(
                            _t(
                                'Could not generate custom range for selected Attribute Field: "%s"'
                            ),
                            indicator
                        ),
                        {
                            type: "warning",
                        }
                    );
                    return false;
                }
                // "RdYlBu" is a set of colors
                scale = chroma.scale("RdYlBu").domain([0, vals.length], vals.length);
                break;
            case "quantile":
                serie.getClassQuantile(nb_class);
                vals = serie.getRanges();
                scale = scale.domain([0, vals.length], vals.length);
                break;
            case "interval":
                serie.getClassEqInterval(nb_class);
                vals = serie.getRanges();
                if (vals.some((item) => item === "0 - 0")) {
                    this.notification.add(
                        sprintf(
                            _t(
                                'Could not generate interval range for selected Attribute Field: "%s"'
                            ),
                            indicator
                        ),
                        {
                            type: "warning",
                        }
                    );
                    return false;
                }
                scale = scale.domain([0, vals.length], vals.length);
                break;
        }
        let colors = [];
        if (cfg.classification === "custom") {
            colors = vals
                .filter((val) => val)
                .map((val) => chroma(val).alpha(opacity).css());
        } else {
            colors = scale
                .colors(vals.length)
                .map((color) => chroma(color).alpha(opacity).css());
        }
        const styles_map = this.createStylesWithColors(colors);
        let legend = null;
        if (vals.length <= LEGEND_MAX_ITEMS) {
            legend = serie.getHtmlLegend(colors, cfg.name, 1);
            for (let i = 0; i < data.length; i++) {
                legend = legend.replace(
                    data[i]._values[cfg.attribute_field_id[1]],
                    data[i]._values.stage_name
                );
            }
        }
        return {
            style: (feature) => {
                const value = feature.get("attributes")[indicator];
                const color_idx = this.getClass(value, vals);
                var label_text = feature.values_.attributes.label;
                if (label_text === false) {
                    label_text = "";
                } else if (label_text !== "") {
                    label_text = feature.values_.attributes.stage_name;
                }
                try {
                    styles_map[colors[color_idx]][0].text_.text_ =
                        label_text.toString();
                } catch {
                    // Do nothing to restore history
                    return;
                }
                return styles_map[colors[color_idx]];
            },
            legend,
        };
    },
    async onLayerChanged(vector, layer) {
        layer.setSource(null);
        const element = document.getElementById(`legend-${vector.resId}`);
        if (element !== null) {
            element.remove();
        }
        if (vector.model) {
            this.cfg_models.push(vector.model);
            const fields_to_read = [vector.geo_field_id[1]];
            if (vector.attribute_field_id) {
                fields_to_read.push(vector.attribute_field_id[1]);
            }
            const data = await this.getModelData(vector, fields_to_read);
            this.styleVectorLayerAndLegend(vector, data, layer);
            this.useRelatedModel(vector, layer, data);
        } else {
            const data = [];
            for (const record of this.props.data.records) {
                if (
                    vector.attribute_field_id[1] === "custom_color" &&
                    typeof record.data[vector.attribute_field_id[1]] === "string"
                ) {
                    record.data[vector.attribute_field_id[1]] = parseInt(
                        record.data[vector.attribute_field_id[1]].split("#")[1],
                        16
                    );
                }
                if (
                    record.data[vector.geo_field_id[1]] !== false &&
                    this._locationLayerMatches(vector, record)
                ) {
                    data.push(record);
                }
            }
            this.styleVectorLayerAndLegend(vector, data, layer);
            this.addSourceToLayer(data, vector, layer);
        }
    },
    addSourceToLayer(res, cfg, lv) {
        const source = new ol.source.Vector();
        this.addFeatureToSource(res, cfg, source);
        lv.setSource(source);
        const geoField = cfg.geo_field_id && cfg.geo_field_id[1];
        if (geoField !== "worker_shape") {
            this.vectorSource = source;
        }
    },
    styleVectorLayerAndLegend(cfg, data, lv) {
        const aux = [];
        for (var i = 0; i < data.length; i++) {
            if (
                cfg.attribute_field_id[1] === "custom_color" &&
                typeof data[i]._values[cfg.attribute_field_id[1]] === "string"
            ) {
                data[i]._values[cfg.attribute_field_id[1]] = parseInt(
                    data[i]._values[cfg.attribute_field_id[1]].split("#")[1],
                    16
                );
            }
            aux.push(data[i]);
        }
        if (this.checkAttributeFieldUsage(cfg, aux)) {
            const styleInfo = this.styleVectorLayer(cfg, aux);
            if (styleInfo) {
                this.initLegend(styleInfo, cfg);
                lv.setStyle(styleInfo.style);
            }
        }
    },
    /**
     * Allows you to find the index of the color to be used according to its value.
     * @param {*} val
     * @param {*} a
     * @returns {Number}
     */
    getClass(val, a) {
        // Classification uniqueValues
        var idx = a.indexOf(val);
        if (idx > -1) {
            return idx;
        }
        // Range classification
        var separator = " - ";
        for (var i = 0; i < a.length; i++) {
            // All classification except uniqueValues
            if (typeof val !== "object" && a[i] && a[i].indexOf(separator) !== -1) {
                var item = a[i].split(separator);
                if (val <= parseFloat(item[1])) {
                    return i;
                }
            } else if (val === a[i]) {
                // Classification uniqueValues
                return i;
            }
        }
    },

    /**
     * Workers use a person icon. Locations and orders keep the circle marker.
     */
    createStylesWithColors(colors) {
        if (this._markerKind !== "worker") {
            return super.createStylesWithColors(colors);
        }
        const stylesMap = {};
        for (const color of colors) {
            if (!color || color in stylesMap) {
                continue;
            }
            const svg = personIconSvg(color);
            stylesMap[color] = [
                new ol.style.Style({
                    image: new ol.style.Icon({
                        src: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`,
                        width: 36,
                        height: 36,
                        anchor: [0.5, 0.5],
                    }),
                    text: this.createStyleText(),
                }),
            ];
        }
        return stylesMap;
    },
});
