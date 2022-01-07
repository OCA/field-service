odoo.define("fsm_gantt.person_filter", function (require) {
    "use strict";

    const TimelineRenderer = require("web_timeline.TimelineRenderer");
    const components = {
        FieldCustomFilterItem: require("fieldservice_timeline.CustomFilterItem"),
    };

    TimelineRenderer.include({
        /**
         * On start
         * @returns this._super()
         */
        start: async function () {
            var self = this;
            var props = self.view.controllerParams.controlPanel.props;
            if (props && props.action && props.action.res_model == "fsm.order") {
                var data = JSON.parse(JSON.stringify(props.fields));
                _.each(data, function (field, i) {
                    data[i].name = i;
                });
                props.fields = data;
                var custom_props = {
                    action: props.action,
                    fields: props.fields,
                    breadcrumbs: props.breadcrumbs,
                    searchMenuTypes: props.searchMenuTypes,
                    view: props.view,
                    searchModel: props.searchModel,
                    views: props.views,
                };
                const _searchPanelWrapper = new components.FieldCustomFilterItem(
                    self.view.config.controlPanel,
                    custom_props
                );

                _searchPanelWrapper.mount(self.$el.find("#user_filer")[0], {
                    position: "first-child",
                });
                self.$el.find("#person_filter").removeClass("o_hidden");
                self.user_filter = true;
            }
            return this._super.apply(this, arguments);
        },
    });
});
