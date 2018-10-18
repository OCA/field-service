# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class District(models.Model):
    _name = 'district'
    _description = 'District'

    name = fields.Char(string='Name')
    region_id = fields.Many2one('region', string='Region')
