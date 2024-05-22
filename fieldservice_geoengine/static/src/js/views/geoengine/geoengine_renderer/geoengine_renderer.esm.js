/** @odoo-module */

/**
 * Copyright 2024 APSL-Nagarro
 */

/* global chroma, geostats  */

import {GeoengineRenderer} from "@base_geoengine/js/views/geoengine/geoengine_renderer/geoengine_renderer.esm";
import {patch} from "@web/core/utils/patch";

/* CONSTANTS */
const DEFAULT_BEGIN_COLOR = "#FFFFFF";
const DEFAULT_END_COLOR = "#000000";
const LEGEND_MAX_ITEMS = 10;
const DEFAULT_NUM_CLASSES = 5;

patch(GeoengineRenderer.prototype, {
    styleVectorLayerColored(cfg, data) {
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
                styles_map[colors[color_idx]][0].text_.text_ = label_text.toString();
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
                data.push(record);
            }
            this.styleVectorLayerAndLegend(vector, data, layer);
            this.addSourceToLayer(data, vector, layer);
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
        const styleInfo = this.styleVectorLayer(cfg, aux);
        this.initLegend(styleInfo, cfg);
        lv.setStyle(styleInfo.style);
    },
});
