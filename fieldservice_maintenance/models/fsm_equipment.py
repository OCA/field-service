# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMEquipment(models.Model):
    _inherit = "fsm.equipment"

    maintenance_equipment_id = fields.Many2one(
        "maintenance.equipment",
        string="Related Maintenance Equipment",
        required=True,
        ondelete="restrict",
        delegate=True,
        auto_join=True,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        MaintenanceEquipement = self.env["maintenance.equipment"]
        for vals in vals_list:
            maintenance_equipment_id = MaintenanceEquipement.create(
                {
                    "name": vals.get("name", False),
                    "is_fsm_equipment": True,
                    "note": vals.get("notes", False),
                    "maintenance_team_id": vals.get("maintenance_team_id", False),
                }
            )
            if maintenance_equipment_id:
                vals.update({"maintenance_equipment_id": maintenance_equipment_id.id})
        return super().create(vals_list)

    def unlink(self):
        equipments = self.mapped("maintenance_equipment_id")
        res = super().unlink()
        for equipment in equipments:
            other = self.env["fsm.equipment"].search(
                [("maintenance_equipment_id", "=", equipment.id)]
            )
            if not other:
                equipment.is_fsm_equipment = False
        return res
