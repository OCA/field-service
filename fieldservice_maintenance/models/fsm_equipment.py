# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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

    @api.model
    def create(self, vals):
        maintenance_team_id = self.env["maintenance.team"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )
        if not maintenance_team_id:
            raise ValidationError(_("At least one maintenance team must be created"))
        maintenance_equipment_id = self.env["maintenance.equipment"].create(
            {
                "name": vals.get("name"),
                "is_fsm_equipment": True,
                "note": vals.get("notes", False),
                "maintenance_team_id": vals.get("maintenance_team_id", False)
                or maintenance_team_id.id,
            }
        )
        if maintenance_equipment_id:
            vals.update({"maintenance_equipment_id": maintenance_equipment_id.id})
        return super().create(vals)

    def unlink(self):
        equipments = self.mapped("maintenance_equipment_id")
        res = super(FSMEquipment, self).unlink()
        for equipment in equipments:
            other = self.env["fsm.equipment"].search(
                [("maintenance_equipment_id", "=", equipment.id)]
            )
            if not other:
                equipment.is_fsm_equipment = False
        return res
