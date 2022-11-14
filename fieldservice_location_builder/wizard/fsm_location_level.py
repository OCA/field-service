# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FSMLocationLevel(models.TransientModel):
    _name = "fsm.location.level"
    _description = "Level in the FSM location tree structure"

    sequence = fields.Integer()
    name = fields.Char(required=True)
    spacer = fields.Char()
    start_number = fields.Integer()
    end_number = fields.Integer()
    total_number = fields.Integer("Total", compute="_compute_total_number")
    tag_ids = fields.Many2many("res.partner.category", string="Tags", readonly=False)
    wizard_id = fields.Many2one("fsm.location.builder.wizard")

    @api.depends("start_number", "end_number")
    def _compute_total_number(self):
        for level_id in self:
            level_id.total_number = 0
            if (
                level_id.start_number is not None
                and level_id.end_number is not None
                and level_id.start_number < level_id.end_number
            ):
                level_id.total_number = level_id.end_number - level_id.start_number + 1
