# Copyright (c) 2020 Pavlov Media <https://www.pavlovmedia.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ChangeLogImpact(models.Model):
    _name = "change.log.impact"
    _order = "log_impact_sequence"
    _description = "Change Log Impact"

    name = fields.Char(string="Impact", required=True)
    description = fields.Text()
    log_impact_sequence = fields.Integer(
        required=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("res.log.impact")
        or 0,
    )
