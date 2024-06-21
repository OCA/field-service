# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FsmEquipmentLogbook(models.Model):
    _name = "fsm.equipment.logbook"
    _description = "Fsm Equipment Logbook"

    event_date = fields.Datetime(default=fields.Datetime.now)
    equipment_status = fields.Char()
    location_id = fields.Many2one("fsm.location")
    equipment_id = fields.Many2one(
        "fsm.equipment", domain="[('location_id', '=', location_id)]"
    )
    type = fields.Selection(
        [
            ("note", "Note"),
            ("equipment", "Equipment"),
            ("location", "Location"),
            ("order", "Order"),
        ],
        default="note",
    )
    res_id = fields.Many2oneReference(
        model_field="res_model", readonly=True, string="Related Document ID"
    )
    res_model = fields.Selection(
        [
            ("fsm.equipment", "Equipment"),
            ("fsm.location", "Location"),
            ("fsm.order", "Order"),
        ],
        readonly=True,
    )
    source = fields.Char(compute="_compute_source")
    source_display_name = fields.Char(compute="_compute_source_display_name")
    origin_status = fields.Char()
    note = fields.Text(string="Content")

    @api.depends("res_model", "res_id")
    def _compute_source(self):
        for rec in self:
            if rec.res_id and rec.res_model:
                rec.source = f"{rec.res_model},{rec.res_id}"
            else:
                rec.source = False

    @api.depends("res_model", "res_id")
    def _compute_source_display_name(self):
        """
        Computed display name for source field.
        Apparently Odoo doesn't support the reference widget in the list view
        so we add this field in order to show the record display name.
        """
        for rec in self:
            if rec.res_id and rec.res_model:
                record = self.env[rec.res_model].browse(rec.res_id)
                rec.source_display_name = record.display_name
            else:
                rec.source_display_name = False

    def _is_valid_equipment_location(self):
        return (
            not self.equipment_id.location_id
            or self.equipment_id.location_id == self.location_id
        )

    @api.onchange("location_id", "equipment_id")
    def _onchange_equipment_id(self):
        for record in self:
            if not record._is_valid_equipment_location():
                record.equipment_id = False
