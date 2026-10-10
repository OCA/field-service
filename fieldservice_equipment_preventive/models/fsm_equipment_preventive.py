# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class FSMEquipmentPreventive(models.Model):
    _name = "fsm.equipment.preventive"
    _description = "Field Service Equipment Preventive Visit"
    _order = "equipment_id, type_id"
    _rec_name = "type_id"

    equipment_id = fields.Many2one(
        "fsm.equipment", required=True, index=True, ondelete="cascade"
    )
    type_id = fields.Many2one(
        "fsm.preventive.type", string="Visit Type", required=True, ondelete="restrict"
    )
    interval = fields.Integer(string="Interval (Months)", required=True, default=12)
    template_id = fields.Many2one(
        "fsm.template", string="Template", help="Work to perform during the visit."
    )
    last_date = fields.Date(string="Last Visit")
    next_date = fields.Date(
        string="Next Visit", compute="_compute_next_date", store=True, index=True
    )

    _sql_constraints = [
        (
            "equipment_type_uniq",
            "unique(equipment_id, type_id)",
            "A visit type can only be listed once per equipment.",
        ),
        ("interval_positive", "check(interval > 0)", "The interval must be positive."),
    ]

    @api.depends("interval", "last_date")
    def _compute_next_date(self):
        today = fields.Date.context_today(self)
        for preventive in self:
            preventive.next_date = (
                preventive.last_date + relativedelta(months=preventive.interval)
                if preventive.last_date
                else today
            )

    def _preventive_sort_key(self):
        """Order of the line in the checklist of a preventive visit."""
        self.ensure_one()
        equipment = self.equipment_id
        return (
            self.next_date,
            equipment.current_location_id.complete_name or "",
            equipment.name or "",
            self.type_id.sequence,
        )
