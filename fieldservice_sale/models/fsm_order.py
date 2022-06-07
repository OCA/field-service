# Copyright (C) 2019 Brian McMaster
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    sale_ids = fields.Many2many(
        "sale.order",
        string="Sale Orders",
        compute="_compute_sales",
        readonly=True,
        copy=False,
    )
    sale_line_ids = fields.One2many(
        "sale.order.line",
        "fsm_order_id",
        copy=False,
    )
    sale_count = fields.Integer(
        compute="_compute_sales",
        readonly=True,
        copy=False,
    )

    @api.depends("sale_line_ids")
    def _compute_sales(self):
        for order in self:
            sales = order.sale_line_ids.mapped("order_id")
            order.sale_ids = sales
            order.sale_count = len(sales)

    def action_view_sales(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("sale.action_orders")
        sales = self.mapped("sale_ids")
        if len(sales) > 1:
            action["domain"] = [("id", "in", sales.ids)]
        elif sales:
            action["views"] = [(self.env.ref("sale.view_order_form").id, "form")]
            action["res_id"] = sales.ids[0]
        return action
