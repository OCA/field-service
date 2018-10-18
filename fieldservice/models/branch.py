# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Branch(models.Model):
    _name = 'branch'
    _description = 'branch'

    name = fields.Char(string='Name')
    district_id = fields.Many2one('district', string='District')
