# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, models
from odoo.exceptions import ValidationError


class MainenanceEquipmentWizard(models.TransientModel):
    _inherit = "maintenance.equipment.wizard"
    _description = "Mainenance Equipment Wizard"

    def get_fsm_equipment_vals(self, maintenance_id):
        if not (maintenance_id.product_id or maintenance_id.lot_id):
            raise ValidationError(
                _(
                    "You must set a Product and Serial Number to Convert \
                               Maintenance Equipment to FSM Equipment"
                )
            )
        res = super().get_fsm_equipment_vals(maintenance_id)
        res.update(
            {
                "product_id": maintenance_id.product_id.id,
                "lot_id": maintenance_id.lot_id.id,
            }
        )
        return res
