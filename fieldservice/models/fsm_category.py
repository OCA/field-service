# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMCategory(models.Model):
    _name = 'fsm.category'
    _description = 'Field Service Person Category'

    name = fields.Char(string='Name', required='True')
    parent_id = fields.Many2one('fsm.category', string='Parent')

    description = fields.Char(string='Description')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Category name already exists!"),
    ]
