# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author: Italo Lopes <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class FSMRecurringOrder(models.Model):
    _inherit = "fsm.recurring"

    def _split_create_by_equipment(self, vals):
        """
        Create an order for each equipment.
        On fieldservice_repair, we create a repair order for each equipment.
        """
        self.ensure_one()
        orders = self.env["fsm.order"]
        for equipment in self.equipment_ids:
            order_vals = vals.copy()
            order_vals["equipment_id"] = equipment.id
            orders |= self.env["fsm.order"].create(order_vals)
        return orders

    def _should_create_by_equipment(self):
        return bool(
            self.fsm_order_template_id
            and self.fsm_order_template_id.type_id
            and self.fsm_order_template_id.type_id.internal_type == "repair"
        )

    def _create_order(self, date):
        # Originally this method return only a single fsm.order.
        # This method has been modified to return multiple fsm.order
        # as we are creating multiple orders based on equipments.
        self.ensure_one()
        if self._should_create_by_equipment():
            vals = self._prepare_order_values(date)
            orders = self._split_create_by_equipment(vals)
            for order in orders:
                order._onchange_template_id()
        else:
            orders = super()._create_order(date)
            orders._onchange_template_id()
        return orders
