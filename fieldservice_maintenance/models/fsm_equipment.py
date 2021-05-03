# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMEquipment(models.Model):
    _inherit = "fsm.equipment"

    maintenance_equipment_id = fields.Many2one(
        "maintenance.equipment",
        string="Related Maintenance Equipment",
        readonly=True,
        ondelete="restrict",
        delegate=True,
        auto_join=True,
        index=True,
    )

    @api.model
    def create(self, vals):
        maintenance_equipment_id = self.env["maintenance.equipment"].create(
            self._prepare_maintenance_vals(vals)
        )
        if maintenance_equipment_id:
            vals.update({"maintenance_equipment_id": maintenance_equipment_id.id})
        res = super().create(vals)
        maintenance_equipment_id.fsm_equipment_id = res.id
        return res

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

    def _prepare_maintenance_vals(self, vals):
        return {
            "name": vals.get("name"),
            "is_fsm_equipment": True,
            "note": vals.get("notes", False),
            "serial_no": vals.get("lot_id", False)
            and self.env["stock.production.lot"].browse(vals.get("lot_id", False)).name,
            "maintenance_team_id": vals.get("maintenance_team_id", False)
            or self.env.ref("maintenance.equipment_team_maintenance").id,
        }
