# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettingsFsmTeam(models.TransientModel):
    _inherit = 'res.config.settings'

    group_red_fsm_team = fields.Boolean(
        string='Manage RedFSM Teams',
        implied_group='red_team_handler.group_red_fsm_team')
