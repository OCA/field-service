# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMPersonCategory(models.Model):
    _name = 'fsm.person.category'
    _description = 'Field Service Person Category'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer('Color Index', default=10)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Category name already exists!"),
    ]
