# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettingsFsmTeam(models.TransientModel):
    _inherit = 'res.config.settings'

    module_fs_support_ticket = fields.Boolean(
        string="Manage FS Support Tickets",
        default=False
    )
