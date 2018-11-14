# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMAgreement(models.Model):
    _name = 'fsm.agreement'
    _description = 'Field Service Agreement'

    name = fields.Char(string='Name', required=True)
    