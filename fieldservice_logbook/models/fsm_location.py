# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class FSMLocation(models.Model):
    _name = "fsm.location"
    _inherit = ["fsm.location", "fsm.equipment.logbook.mixin"]

    def _read_group_logbook_data(self, logbook: models.BaseModel) -> list:
        return logbook.read_group(
            [
                "|",
                ("location_id", "in", self.ids),
                ("equipment_id.location_id", "in", self.ids),
                ("type", "=", "location"),
            ],
            ["location_id"],
            ["location_id"],
        )

    def _map_logbook_data(self, logbook: models.BaseModel, data: list) -> dict:
        return {
            db["location_id"][0]: logbook.search(
                [
                    "|",
                    ("location_id", "=", db["location_id"][0]),
                    ("equipment_id.location_id", "=", db["location_id"][0]),
                ]
            )
            for db in data
        }

    def _prepare_log_values(self):
        values = super()._prepare_log_values()
        values.update(
            {
                "location_id": self.id,
                "type": "location",
                "res_model": "fsm.location",
            }
        )
        return values

    def write(self, vals):
        res = super().write(vals)
        if vals.get("stage_id"):
            self._create_equipment_log()
        return res
