# Copyright 2024 - TODAY, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Agreement(models.Model):
    _inherit = "agreement"

    sale_order_count = fields.Integer(
        compute="_compute_sale_order_count", string="# Sale Orders"
    )

    def _compute_sale_order_count(self):
        SaleOrder = self.env["sale.order"]
        for agreement in self:
            agreement.sale_order_count = SaleOrder.search_count(
                [("agreement_id", "=", agreement.id)]
            )

    def action_view_sale_order(self):
        self.ensure_one()
        sale_orders = self.env["sale.order"].search([("agreement_id", "=", self.id)])
        action = self.env["ir.actions.act_window"]._for_xml_id("sale.action_quotations")
        if len(sale_orders) == 1:
            form_view = self.env.ref("sale.view_order_form")
            action["views"] = [(form_view.id, "form")]
            action["res_id"] = sale_orders.id
        else:
            action["domain"] = [("id", "in", sale_orders.ids)]
        return action
