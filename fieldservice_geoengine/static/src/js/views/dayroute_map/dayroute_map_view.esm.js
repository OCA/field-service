/** @odoo-module **/

import {RelationalModel} from "@web/model/relational_model/relational_model";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";

import {DayrouteMapArchParser} from "./dayroute_map_arch_parser.esm";
import {DayrouteMapController} from "./dayroute_map_controller.esm";
import {DayrouteMapRenderer} from "./dayroute_map_renderer.esm";

export const dayrouteMapView = {
    type: "dayroute_map",
    display_name: _t("Map"),
    icon: "fa fa-globe",
    multiRecord: true,
    searchMenuTypes: ["filter", "favorite"],
    ArchParser: DayrouteMapArchParser,
    Controller: DayrouteMapController,
    Model: RelationalModel,
    Renderer: DayrouteMapRenderer,

    props: (genericProps, view) => {
        const {arch, relatedModels, resModel} = genericProps;
        const archInfo = new view.ArchParser().parse(arch, relatedModels, resModel);
        return {
            ...genericProps,
            Model: view.Model,
            Renderer: view.Renderer,
            archInfo,
        };
    },
};

registry.category("views").add("dayroute_map", dayrouteMapView);
