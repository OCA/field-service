# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class MainenanceEquipmentWizard(models.TransientModel):
    _name = "maintenance.equipment.wizard"
    _description = "Maintenance Equipment Wizard"

    def convert_maintenance_equipment_fsm(self):
        maintenance_equipments = self.env["maintenance.equipment"].browse(
            self._context.get("active_ids", [])
        )
        for equipment in maintenance_equipments:
            if not equipment.product_id or not equipment.serial_no:
                raise UserError(
                    _(
                        """
                To convert maintenance equipment %s to an FSM Equipment,
                you must assign a Product and a Serial No
                """
                    )
                    % equipment.name
                )
            fsm_vals = self.get_fsm_equipment_vals(equipment)
            self.env["fsm.equipment"].create(fsm_vals)
            equipment.is_fsm_equipment = True

    def get_fsm_equipment_vals(self, equipment):
        lot_id = self.env["stock.production.lot"].search(
            [
                ("name", "=", equipment.serial_no),
                ("product_id", "=", equipment.product_id.id),
            ]
        )
        if not lot_id:
            lot_id = self.env["stock.production.lot"].create(
                {
                    "name": equipment.serial_no,
                    "product_id": equipment.product_id.id,
                    "company_id": equipment.company_id.id,
                }
            )
        return {
            "name": equipment.name,
            "company_id": equipment.company_id.id,
            "product_id": equipment.product_id.id,
            "lot_id": lot_id.id,
            "maintenance_equipment_id": equipment.id,
            "maintenance_team_id": equipment.maintenance_team_id.id,
        }
