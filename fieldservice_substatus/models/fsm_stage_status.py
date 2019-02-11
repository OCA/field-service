# Copyright (C) 2019 - TODAY, Open Source Integrators, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMStageStatus(models.Model):
    _name = 'fsm.stage.status'
    _description = 'Order Sub-Status'

    name = fields.Char(string='Name', required=True)
