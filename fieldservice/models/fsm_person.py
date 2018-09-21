# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMPerson(models.Model):
    _name = 'fsm.person'
    _inherit = 'res.partner'
    _description = 'Field Service Person'

    name = fields.Char(string='Name', size=35, required=True)