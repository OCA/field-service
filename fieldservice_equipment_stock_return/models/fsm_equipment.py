# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author: Italo Lopes <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class FSMEquipment(models.Model):
    _inherit = "fsm.equipment"

    def create_equipment_order_return(self):
        self.ensure_one()
        order_type = self.env.ref(
            "fieldservice_equipment_stock_return.fsm_order_type_return",
            raise_if_not_found=False,
        )
        if not order_type:
            order_type = self.env["fsm.order.type"].search(
                [("internal_type", "=", "return")], limit=1
            )
            if not order_type:
                raise ValidationError(_("No return order type found."))
        return {
            "name": "Return Equipment",
            "type": "ir.actions.act_window",
            "res_model": "fsm.order",
            "view_mode": "form",
            "context": {
                "default_equipment_id": self.id,
                "default_type": order_type and order_type.id or False,
            },
        }
