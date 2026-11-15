# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FieldServiceBlackoutDay(models.Model):
    _name = "fsm.blackout.day"
    _description = "Blackout Days (No Service)"

    name = fields.Char(string="Description", required=True)
    date = fields.Date(string="Blackout Day", required=True)
    zip = fields.Char(
        help="Postal code of the blackout day.",
    )

    _unique_blackout_day_zip = models.Constraint(
        "unique(date, zip)",
        "A blackout day for this date and ZIP code already exists!",
    )

    @api.constrains("date", "zip")
    def _check_unique_date_zip(self):
        for record in self:
            domain = [
                ("id", "!=", record.id),
                ("date", "=", record.date),
                ("zip", "=", record.zip or False),
            ]
            if self.search_count(domain):
                raise ValidationError(
                    self.env._(
                        "A blackout day for this date and ZIP code already exists!"
                    )
                )
