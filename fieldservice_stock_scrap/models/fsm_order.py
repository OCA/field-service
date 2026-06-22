# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    scrap_ids = fields.One2many(
        "stock.scrap",
        "fsm_order_id",
        string="Scrap Operations",
    )
    scrap_count = fields.Integer(string="Scrap Orders", compute="_compute_scrap_ids")

    @api.depends("scrap_ids")
    def _compute_scrap_ids(self):
        for order in self:
            order.scrap_count = len(self.scrap_ids.ids)

    def action_view_scraps(self):
        return {
            "name": _("Scraps from FieldService order ") + self.name,
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "stock.scrap",
            "domain": [("id", "in", self.scrap_ids.ids)],
        }

    def action_scrap_stock(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Scrap"),
            "res_model": "scrap.stock.wizard",
            "target": "new",
            "view_mode": "form",
            "context": {"fsm_order_id": self.id},
        }
