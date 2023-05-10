# Copyright (C) 2019 Brian McMaster
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    sale_id = fields.Many2one("sale.order")
    sale_line_id = fields.Many2one("sale.order.line")

    def action_view_sales(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "views": [[False, "form"]],
            "res_id": self.sale_line_id.order_id.id or self.sale_id.id,
            "context": {"create": False},
            "name": _("Sales Orders"),
        }

    def write(self, vals):
        for order in self:
            if "customer_id" not in vals and not order.customer_id:
                vals.update({"customer_id": order.sale_id.partner_id.id})
        return super(FSMOrder, self).write(vals)

    def create(self, vals):
        sale_id = self.env["sale.order"].browse(vals.get("sale_id"))
        if sale_id:
            vals["customer_id"] = sale_id.partner_id.id
        return super(FSMOrder, self).create(vals)
