# Copyright (C) 2022 Rafnix Guzman
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FsmEquipment(models.Model):
    _inherit = "fsm.equipment"

    location_history_ids = fields.One2many(
        "fsm.equipment.location.history", "equipment_id", string="Location History"
    )

    def action_create_location_history(self):
        self.ensure_one()
        return {
            "name": "Transfer Equipment",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "fsm.equipment.location.history",
            "context": {
                "default_equipment_id": self.id,
                "default_from_location_id": self.current_stock_location_id.id,
                "default_date": fields.Datetime.now(),
            },
            "target": "new",
        }
