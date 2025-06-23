# Copyright 2025 APSL-Nagarro Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FieldServiceBlackoutDay(models.Model):
    _inherit = "fsm.blackout.day"

    zip = fields.Char(
        help="Postal code of the blackout day.",
    )
