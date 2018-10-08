# -*- coding: utf-8 -*-

from odoo import fields, models


# team members
class TeamMembers(models.Model):
    _name = 'fsm.team.members'

    name = fields.Many2one(
            'fsm.person',
            string="Person"
    )
    team_id = fields.Many2one(
            'fsm.teams',
            string="Team"
    )
    available = fields.Boolean(
            string="Available",
            default=True,
            related='name.available'
    )
