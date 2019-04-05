# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMTeam(models.Model):
    _name = 'fsm.team'
    _description = 'Field Service Team'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_stages(self):
        return self.env['fsm.stage'].search([('is_default', '=', True)])

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
        string="Orders Count")
    order_need_assign_count = fields.Integer(
        compute='_compute_order_need_assign_count',
        string="Orders to Assign")
    order_need_schedule_count = fields.Integer(
        compute='_compute_order_need_schedule_count',
        string="Orders to Schedule")
    sequence = fields.Integer('Sequence', default=1,
                              help="Used to sort teams. Lower is better.")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Team name already exists!"),
    ]


class FSMStage(models.Model):
    _inherit = 'fsm.stage'

    def _default_team_ids(self):
        default_team_id = self.env.context.get('default_team_id')
        return [default_team_id] if default_team_id else None

    team_ids = fields.Many2many(
        'fsm.team', 'order_team_stage_rel', 'stage_id', 'team_id',
        string='Teams', default=_default_team_ids)
