# Copyright (c) 2020 Pavlov Media <https://www.pavlovmedia.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ChangeLogStage(models.Model):
    _name = "change.log.stage"
    _order = "stage_sequence"
    _description = "Change Log Stage"

    name = fields.Char(string="Stage", required=True)
    description = fields.Text()
    fold = fields.Boolean(string="Folded")
    is_close = fields.Boolean(string="Closing Kanban Stage")
    stage_sequence = fields.Integer(
        required=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("res.log.impact")
        or 0,
    )
