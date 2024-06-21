# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class FsmEquipmentLogbookMixin(models.AbstractModel):
    _name = "fsm.equipment.logbook.mixin"
    _description = "Fsm Equipment Logbook Mixin"

    equipment_logs_count = fields.Integer(compute="_compute_equipment_logs")
    equipment_logs_ids = fields.Many2many(
        "fsm.equipment.logbook", compute="_compute_equipment_logs"
    )

    def _read_group_logbook_data(self, logbook: models.BaseModel) -> list:
        raise NotImplementedError(
            "In order to use fsm.equipment.logbook.mixin, "
            "method _read_group_logbook_data must be implemented"
        )

    def _map_logbook_data(self, logbook: models.BaseModel, data: list) -> dict:
        raise NotImplementedError(
            "In order to use fsm.equipment.logbook.mixin, "
            "method _map_logbook_data must be implemented"
        )

    def _read_group_logbook(self, logbook: models.BaseModel):
        """Given a logbook, return the data fetched by _read_group.

        _read_group_logbook_data to be implemented in the model that uses this mixin.
        """
        return self._read_group_logbook_data(logbook)

    def _get_mapped_logbook_data(self, logbook: models.BaseModel, data: list):
        """Given a logbook and data fetched by _read_group,
        return the mapping between the record and equipment logs.

        _map_logbook_data to be implemented in the model that uses this mixin.
        """
        return self._map_logbook_data(logbook, data)

    @api.depends("stage_id")
    def _compute_equipment_logs(self):
        logbook = self.sudo().env["fsm.equipment.logbook"]
        logbook_data = self._read_group_logbook(logbook)
        logbook_mapped_data = self._get_mapped_logbook_data(logbook, logbook_data)
        for record in self:
            # for the `fsm.order` model we need to map by location_id
            if record._name == "fsm.order":
                equipment_logs = logbook_mapped_data.get(record.location_id.id, logbook)
            else:
                equipment_logs = logbook_mapped_data.get(record.id, logbook)
            record.equipment_logs_count = len(equipment_logs)
            record.equipment_logs_ids = equipment_logs

    def _prepare_log_values(self):
        """Return the values to create a logbook entry"""
        self.ensure_one()
        return {
            "origin_status": self.stage_id.name,
            "note": self.name,
            "res_id": self.id,
        }

    @api.model
    def _create_equipment_log(self):
        """Return a logbook entries for the record"""
        return self.env["fsm.equipment.logbook"].create(
            [rec._prepare_log_values() for rec in self]
        )

    def action_view_equipment_logs(self):
        return {
            "name": _("Equipment Logbook"),
            "type": "ir.actions.act_window",
            "res_model": "fsm.equipment.logbook",
            "view_type": "list",
            "view_mode": "list,form",
            "domain": [("id", "in", self.equipment_logs_ids.ids)],
            "context": {
                "search_default_equipment_groupby": 1,
                "search_default_location_groupby": 1,
            },
            "target": "current",
        }
