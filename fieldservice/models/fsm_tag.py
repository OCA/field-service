# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMTag(models.Model):
    _name = 'fsm.tag'
    _description = 'Field Service Tag'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer('Color Index', default=10)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]
