# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Territory(models.Model):
    _name = 'territory'
    _description = 'Territory'

    name = fields.Char(string='Name')
    branch_id = fields.Many2one('branch', string='Branch')
