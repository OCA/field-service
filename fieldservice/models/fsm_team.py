# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMTeam(models.Model):
    _name = 'fsm.team'
    _description = 'Field Service Team'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_stages(self):
        Stage = self.env['fsm.stage']
        return Stage.search([('is_default', '=', True)])

    def _compute_order_count(self):
        order_data = self.env['fsm.order'].read_group(
            [('team_id', 'in', self.ids), ('stage_id.is_closed', '=', False)],
            ['team_id'], ['team_id'])
        result = {data['team_id'][0]: int(data['team_id_count'])
                  for data in order_data}
        for team in self:
            team.order_count = result.get(team.id, 0)

    def _compute_order_need_assign_count(self):
        order_data = self.env['fsm.order'].read_group(
            [('team_id', 'in', self.ids), ('person_id', '=', False)],
            ['team_id'], ['team_id'])
        result = {data['team_id'][0]: int(data['team_id_count'])
                  for data in order_data}
        for team in self:
            team.order_need_assign_count = result.get(team.id, 0)

    def _compute_order_need_schedule_count(self):
        order_data = self.env['fsm.order'].read_group(
            [('team_id', 'in', self.ids),
             ('scheduled_date_start', '=', False)],
            ['team_id'], ['team_id'])
        result = {data['team_id'][0]: int(data['team_id_count'])
                  for data in order_data}
        for team in self:
            team.order_need_schedule_count = result.get(team.id, 0)

    name = fields.Char(required=True, translation=True)
    description = fields.Text(translation=True)
    color = fields.Integer('Color Index')
    stage_ids = fields.Many2many(
        'fsm.stage', 'order_team_stage_rel', 'team_id', 'stage_id',
        string='Stages', default=_default_stages)
    order_count = fields.Integer(
        compute='_compute_order_count',
        string="Orders")
    order_need_assign_count = fields.Integer(
        compute='_compute_order_need_assign_count',
        string="Orders to Assign")
    order_need_schedule_count = fields.Integer(
        compute='_compute_order_need_schedule_count',
        string="Orders to Schedule")
    order_ids = fields.One2many(
        'fsm.order', 'team_id', string='Orders',
        domain=[('stage_id.is_closed', '=', False)])
    sequence = fields.Integer('Sequence', default=1,
                              help="Used to sort teams. Lower is better.")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.user.company_id)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Team name already exists!"),
    ]
