# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import webcolors


class FSMStage(models.Model):
    _inherit = 'fsm.stage'

    choose_color = fields.Char("Choose stage color", default="red")

    @api.onchange('choose_color')
    def _onchange_choose_color(self):
        if self.choose_color:
            self.custom_color = webcolors.name_to_hex(
                self.choose_color)
