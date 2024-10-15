/** @odoo-module */

import "portal.portal"; // Force dependencies
import publicWidget from "web.public.widget";

publicWidget.registry.PortalHomeCounters.include({
    /**
     * @override
     */
    _getCountersAlwaysDisplayed() {
        return this._super(...arguments).concat(["fsm_order_count"]);
    },
});
