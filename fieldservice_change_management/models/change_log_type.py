# Copyright (c) 2020 Pavlov Media <https://www.pavlovmedia.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ChangeLogType(models.Model):
    _name = "change.log.type"
    _order = "log_type_sequence"
    _description = "Change Log Type"

    name = fields.Char(string="Type", required=True)
    description = fields.Text()
    log_type_sequence = fields.Integer(
        required=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("res.log.impact")
        or 0,
    )
