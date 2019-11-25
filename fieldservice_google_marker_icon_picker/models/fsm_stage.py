# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMStage(models.Model):
    _inherit = 'fsm.stage'

    custom_color = fields.Char("Choose Color", default="red")
