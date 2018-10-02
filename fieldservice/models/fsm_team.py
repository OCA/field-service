# Copyright (C) 2018 - TODAY, Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMTeam(models.Model):
    _name = 'fsm.team'
    _description = 'Field Service Team'

    def _default_stages(self):
        Stage = self.env['fsm.stage']
        return Stage.search([('is_default', '=', True)])

    name = fields.Char(equired=True, translation=True)
    description = fields.Text(translation=True)
    stage_ids = fields.Many2many(
        'fsm.stage', 
        string='Stages',
        default=_default_stages)


    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Team name already exists!"),
    ]
