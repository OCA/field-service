# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettingsFsmTeam(models.TransientModel):
    _inherit = 'res.config.settings'

    group_fsm_teams = fields.Boolean(
        string='Manage FSM Teams',
        implied_group='fsm_team_handler.group_fsm_teams')
