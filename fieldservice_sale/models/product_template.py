# Copyright (C) 2019 Brian McMaster
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    service_type = fields.Selection(
        selection_add=[
            ("field", "Field Service Orders"),
        ],
        ondelete={"field": "cascade"},
    )
    field_service_tracking = fields.Selection(
        [
            ("no", "Don't create FSM order"),
            ("sale", "Create one FSM order per sale order"),
            ("line", "Create one FSM order per sale order line"),
        ],
        string="Field Service Tracking",
        default="no",
        help="""Determines what happens upon sale order confirmation:
                - None: nothing additional, default behavior.
                - Per Sale Order: One FSM Order will be created for the sale.
                - Per Sale Order Line: One FSM Order for each sale order line
                will be created.""",
    )
    fsm_order_template_id = fields.Many2one(
        "fsm.template",
        "Field Service Order Template",
        help="Select the field service order template to be created",
    )

    @api.onchange("field_service_tracking")
    def _onchange_field_service_tracking(self):
        if self.field_service_tracking == "no":
            self.fsm_order_template_id = False
