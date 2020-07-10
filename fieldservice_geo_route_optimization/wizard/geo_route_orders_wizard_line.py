# Copyright (C) 2020 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMGeoRouteOrdersLine(models.TransientModel):
    _name = 'fsm.geo.route.orders.line'
    _description = 'Geo Route FSM Order Lines'

    sequence = fields.Integer('Sequence', default=1)
    fsm_order_id = fields.Many2one('fsm.order', string='FSM Order')
    fsm_order_location = fields.Many2one(
        'fsm.location', related='fsm_order_id.location_id')
    duration_from_previous = fields.Integer('Drive Time from Previous')
