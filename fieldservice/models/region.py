# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Region(models.Model):
    _name = 'region'
    _description = 'Region'

    name = fields.Char(string='Name')
