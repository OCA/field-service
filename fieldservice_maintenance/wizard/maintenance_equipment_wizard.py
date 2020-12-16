# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class MainenanceEquipmentWizard(models.TransientModel):
    _name = "maintenance.equipment.wizard"
    _description = "Mainenance Equipment Wizard"

    def convert_maintenance_equipment_fsm(self):
        maintenance_equpment_ids = self.env["maintenance.equipment"].browse(
            self._context.get("active_ids", [])
        )
        for maintenance_id in maintenance_equpment_ids:
            if not (maintenance_id.product_id or maintenance_id.lot_id):
                raise UserError(
                    _(
                        "To convert maintenance equipment %s"
                        "to an FSM Equipment, "
                        "you must assign a Product and "
                        "a Serial No"
                    )
                    % maintenance_id.name
                )
            fsm_vals = self.get_fsm_equipment_vals(maintenance_id)
            fsm_equipment = self.env["fsm.equipment"].create(fsm_vals)
            maintenance_id.is_fsm_equipment = True
            maintenance_id.fsm_equipment_id = fsm_equipment.id

    def get_fsm_equipment_vals(self, maintenance_id):
        return {
            "name": maintenance_id.name,
            "company_id": maintenance_id.company_id.id,
            "maintenance_equipment_id": maintenance_id.id,
            "maintenance_team_id": maintenance_id.maintenance_team_id.id,
        }
