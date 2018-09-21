# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMRoute(models.Model):
    _name = 'fsm.route'
    _description = 'Field Service Route'

    name = fields.Char(string='Name')
    fsm_order_ids = fields.One2many('fsm.order', 'fsm_route_id',
                                    string='Orders')
    fsm_person_id = fields.Many2one('fsm.person',
                                    string='Field Service Person')
    date = fields.Date(string='Date')
