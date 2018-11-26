# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrderTemplate(models.Model):
    _name = 'fsm.order.template'
    _description = 'Field Service Order Template'

    name = fields.Char(string='Name', required=True)
    category_ids = fields.Many2many(
        'fsm.person.category', string='Categories')
