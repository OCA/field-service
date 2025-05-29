odoo.define("fsm_create_so.kanban_button", function (require) {
    "use strict";
    var KanbanController = require("web.KanbanController");
    var KanbanView = require("web.KanbanView");
    var viewRegistry = require("web.view_registry");
    var KanbanButton = KanbanController.include({
        buttons_template: "fsm_create_so.button",
        events: _.extend({}, KanbanController.prototype.events, {
            "click .open_wizard_action_kanban": "_OpenWizardKanban",
        }),
        _OpenWizardKanban: function () {
            this.do_action({
                type: "ir.actions.act_window",
                res_model: "fsm.create.so.wizard",
                name: "Create Sales Order",
                view_mode: "form",
                view_type: "form",
                views: [[false, "form"]],
                target: "new",
                res_id: false,
            });
        },
    });
    var SaleOrderKanbanView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: KanbanButton,
        }),
    });
    viewRegistry.add("fsm_create_so_button", SaleOrderKanbanView);
});
