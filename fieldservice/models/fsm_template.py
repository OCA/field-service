# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMTemplate(models.Model):
    _name = 'fsm.template'
    _description = 'Field Service Order Template'

    name = fields.Char(string="Name", required=True)
    instructions = fields.Text(string="Instructions")
    category_ids = fields.Many2many('fsm.category', string="Categories")
    hours = fields.Float(string="Hours")
