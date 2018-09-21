# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMLocation(models.Model):
    _name = 'fsm.location'
    _inherit = 'res.partner'
    _description = 'Field Service Location'

    name = fields.Char(string='Name')
    type = fields.Char(string='Type', size=35)
    description = fields.Char(string='Description')
