from odoo import fields, models


# team members
class TeamMembers(models.Model):
    _name = 'fsm.team.member'

    name = fields.Many2one('fsm.person',
                           string="Person"
                           )
    team_id = fields.Many2one('fsm.teams',
                              string="Team"
                              )
    available = fields.Boolean(string="Engaged",
                               default=True,
                               related='name.available'
                               )
