# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMRegion(models.Model):
    _name = 'fsm.region'
    _description = 'Region'

    name = fields.Char(string='Name')
    description = fields.Char(string='Description')
    partner_id = fields.Many2one('res.partner', string='Region Manager')
