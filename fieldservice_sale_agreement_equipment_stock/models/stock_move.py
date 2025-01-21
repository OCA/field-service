# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def prepare_equipment_values(self, move_line):
        # OVERRIDE: Propagate the agreement_id from the Sale Order to the FSM Equipment
        res = super().prepare_equipment_values(move_line)
        if sale := move_line.move_id.sale_line_id.order_id:
            res.update({"agreement_id": sale.agreement_id.id})
        return res
