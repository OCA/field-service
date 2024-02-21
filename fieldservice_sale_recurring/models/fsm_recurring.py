# Copyright (C) 2019 Brian McMaster
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class FSMRecurring(models.Model):
    _inherit = "fsm.recurring"

    sale_line_id = fields.Many2one("sale.order.line")

    def action_view_sales(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "views": [[False, "form"]],
            "res_id": self.sale_line_id.order_id.id,
            "context": {"create": False},
            "name": _("Sales Orders"),
        }

    def _prepare_order_values(self, date=None):
        res = super()._prepare_order_values(date)
        res["sale_line_id"] = self.sale_line_id.id
        return res
