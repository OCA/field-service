# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FieldServiceStressDay(models.Model):
    _name = "fsm.stress.day"
    _description = "High-Demand Days"

    name = fields.Char(string="Description", required=True)
    date = fields.Date(string="Stress Day", required=True)

    _sql_constraints = [
        (
            "unique_stress_day",
            "unique(date)",
            "A stress day with this date already exists!",
        )
    ]
