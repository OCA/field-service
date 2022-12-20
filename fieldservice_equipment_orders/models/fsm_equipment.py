# Copyright 2022 Rafnix Guzman
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FsmEquimentOrders(models.Model):

    _inherit = "fsm.equipment"

    fsm_order_ids = fields.One2many("fsm.order", "equipment_id", "Orders")

    fsm_order_count = fields.Integer(compute="_compute_fsm_order_count")

    def _compute_fsm_order_count(self):
        for fsm_equipment in self:
            fsm_equipment.fsm_order_count = len(fsm_equipment.fsm_order_ids)

    def smart_button_fsm_orders(self):
        self.ensure_one()

        result = self.env["ir.actions.act_window"]._for_xml_id(
            "fieldservice.action_fsm_dash_order"
        )
        result.update(
            {
                "domain": [("id", "in", self.fsm_order_ids.ids)],
            }
        )
        return result
