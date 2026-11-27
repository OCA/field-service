# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FSMEquipment(models.Model):
    _inherit = "fsm.equipment"

    preventive_ids = fields.One2many(
        "fsm.equipment.preventive", "equipment_id", string="Preventive Visits"
    )
    next_preventive_date = fields.Date(
        string="Next Preventive Visit",
        compute="_compute_next_preventive_date",
        store=True,
        index=True,
    )

    @api.depends("preventive_ids.next_date")
    def _compute_next_preventive_date(self):
        for equipment in self:
            dates = equipment.preventive_ids.filtered("next_date").mapped("next_date")
            equipment.next_preventive_date = min(dates) if dates else False
