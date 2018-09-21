# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMStage(models.Model):
    _name = 'fsm.stage'
    _description = 'Field Service Stage'

    name = fields.Char(string='Name', required=True)
