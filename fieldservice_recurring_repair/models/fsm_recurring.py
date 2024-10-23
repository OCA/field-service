# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class FSMRecurringOrder(models.Model):
    _inherit = "fsm.recurring"

    def _split_create(self, vals):
        self.ensure_one()
        orders = self.env["fsm.order"]
        for equipment in self.equipment_ids:
            order_vals = vals.copy()
            order_vals["equipment_id"] = equipment.id
            orders |= self.env["fsm.order"].create(order_vals)
        return orders

    def _check_split_create(self):
        return bool(
            self.fsm_order_template_id
            and self.fsm_order_template_id.type_id
            and self.fsm_order_template_id.type_id.internal_type == "repair"
        )

    def _create_order(self, date):
        self.ensure_one()
        vals = self._prepare_order_values(date)
        if self._check_split_create():
            orders = self._split_create(vals)
            for order in orders:
                order._onchange_template_id()
        else:
            orders = super()._create_order(date)
            orders._onchange_template_id()
        return orders
