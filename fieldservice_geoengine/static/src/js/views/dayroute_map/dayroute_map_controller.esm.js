/** @odoo-module **/

import {Component, useState} from "@odoo/owl";
import {Layout} from "@web/search/layout";
import {SearchBar} from "@web/search/search_bar/search_bar";
import {extractFieldsFromArchInfo} from "@web/model/relational_model/utils";
import {session} from "@web/session";
import {standardViewProps} from "@web/views/standard_view_props";
import {useModelWithSampleData} from "@web/model/model";
import {usePager} from "@web/search/pager_hook";
import {useSearchBarToggler} from "@web/search/search_bar/search_bar_toggler";
import {useService} from "@web/core/utils/hooks";

export class DayrouteMapController extends Component {
    static template = "fieldservice_geoengine.DayrouteMapController";
    static components = {Layout, SearchBar};
    static props = {...standardViewProps};

    setup() {
        this.action = useService("action");
        this.archInfo = this.props.archInfo;
        this.model = useState(
            useModelWithSampleData(this.props.Model, this.modelParams)
        );
        this.searchBarToggler = useSearchBarToggler();
        usePager(() => {
            const list = this.model.root;
            const {count, limit, offset} = list;
            return {
                offset,
                limit,
                total: count,
                onUpdate: async ({offset, limit}) => {
                    await list.load({limit, offset});
                    this.render(true);
                },
            };
        });
    }

    get modelParams() {
        const {resModel, fields, archInfo, limit} = this.props;
        const extracted = extractFieldsFromArchInfo(archInfo, fields);
        let {activeFields} = extracted;
        if (!("id" in activeFields)) {
            activeFields = {...activeFields, id: {readonly: "True"}};
        }
        return {
            config: {
                resModel,
                fields: extracted.fields,
                activeFields,
            },
            limit: archInfo.limit || limit || 80,
            activeIdsLimit: session.active_ids_limit,
            hooks: {},
        };
    }

    openDayroute(resId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "fsm.route.dayroute",
            res_id: resId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}
