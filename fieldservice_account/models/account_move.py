# Copyright (C) 2018, Open Source Integrators
# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    fsm_order_ids = fields.Many2many(
        "fsm.order",
        compute="_compute_fsm_order_ids",
        string="Field Service orders associated to this invoice",
    )
    fsm_order_count = fields.Integer(
        string="FSM Orders", compute="_compute_fsm_order_ids"
    )

    @api.depends("line_ids")
    def _compute_fsm_order_ids(self):
        for order in self:
            orders = self.env["fsm.order"].search(
                [("invoice_lines", "in", order.line_ids.ids)]
            )
            order.fsm_order_ids = orders
            order.fsm_order_count = len(order.fsm_order_ids)

    def action_view_fsm_orders(self):
        xmlid = "fieldservice.action_fsm_dash_order"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        orders = self.fsm_order_ids
        if len(orders) > 1:
            action["domain"] = [("id", "in", orders.ids)]
        elif orders:
            action["views"] = [(self.env.ref("fieldservice.fsm_order_form").id, "form")]
            action["res_id"] = orders.id
        return action
