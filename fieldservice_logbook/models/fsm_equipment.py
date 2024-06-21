# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class FSMEquipment(models.Model):
    _name = "fsm.equipment"
    _inherit = ["fsm.equipment", "fsm.equipment.logbook.mixin"]

    def _read_group_logbook_data(self, logbook: models.BaseModel) -> list:
        return logbook.read_group(
            [
                "|",
                ("equipment_id", "child_of", self.ids),
                ("equipment_id", "in", self.ids),
                ("type", "=", "equipment"),
            ],
            ["equipment_id"],
            ["equipment_id"],
        )

    def _map_logbook_data(self, logbook: models.BaseModel, data: list) -> dict:
        return {
            db["equipment_id"][0]: logbook.search(
                [
                    "|",
                    ("equipment_id", "=", db["equipment_id"][0]),
                    ("equipment_id", "child_of", db["equipment_id"][0]),
                ]
            )
            for db in data
        }

    def _prepare_log_values(self):
        values = super()._prepare_log_values()
        values.update(
            {
                "equipment_status": self.stage_id.name,
                "location_id": self.location_id.id,
                "equipment_id": self.id,
                "type": "equipment",
                "res_model": "fsm.equipment",
            }
        )
        return values

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.filtered("stage_id")._create_equipment_log()
        return records

    def write(self, vals):
        res = super().write(vals)
        if vals.get("stage_id"):
            self._create_equipment_log()
        return res
