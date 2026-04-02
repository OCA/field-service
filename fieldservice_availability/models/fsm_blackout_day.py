# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FieldServiceBlackoutDay(models.Model):
    _name = "fsm.blackout.day"
    _description = "Blackout Days (No Service)"

    name = fields.Char(string="Description", required=True)
    date = fields.Date(string="Blackout Day", required=True)

    _fsm_blackout_day_date_uniq = models.Constraint(
        "UNIQUE(date)",
        "A blackout day with this date already exists!",
    )
