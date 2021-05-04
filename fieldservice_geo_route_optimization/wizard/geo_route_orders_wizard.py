# Copyright (C) 2020 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FSMGeoRouteOrders(models.TransientModel):
    _name = 'fsm.geo.route.orders.wizard'
    _description = 'Geo Route FSM Orders'

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            res['fsm_order_ids'] = [(6, 0, active_ids)]
        return res

    fsm_order_ids = fields.Many2many(
        'fsm.order',
        string='FSM Orders to Sort',
    )
    depot_partner_id = fields.Many2one(
        'res.partner',
        string='Depot',
    )
    wizard_stage = fields.Selection([
        ('new', 'New'),
        ('sorted', 'Sorted')],
        default='new', string='Stage',
    )
    order_wizard_line_ids = fields.Many2many(
        'fsm.geo.route.orders.line',
        string='FSM Order Line',
    )
    start_date = fields.Datetime(
        string='Start Date and Time',
    )

    def _populate_lines(self, data):
        sorted_ids = data['sorted_ids']
        durations = data['durations']
        line_ids = []
        Line = self.env['fsm.geo.route.orders.line']
        for i in range(len(sorted_ids)):
            line_ids.append(
                Line.create({
                    'sequence': i + 1,
                    'fsm_order_id': sorted_ids[i],
                    'duration_from_previous': durations[i],
                }).id
            )
        self.order_wizard_line_ids = [(6, 0, line_ids)]

    def action_optimize(self):
        depot = self.depot_partner_id
        if not depot:
            raise UserError(_('You must provide a depot from'
                              ' which the route will start and end'))
        orders = self.fsm_order_ids
        origin_address = depot._display_address(True)
        origin_address = origin_address.replace(' ', '+').replace('\n', '+')
        optimized_dict = orders.optimize_records(origin_address)
        self._populate_lines(optimized_dict)
        self.wizard_stage = 'sorted'
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_schedule(self):
        start = self.start_date
        if not start:
            raise UserError(_('You must provide a start date from'
                              ' which orders will be scheduled'))
        for line in self.order_wizard_line_ids:
            start += relativedelta(seconds=line.duration_from_previous)
            line.fsm_order_id.write({
                'scheduled_date_start': start,
            })
            start = line.fsm_order_id.scheduled_date_end
        orders = self.order_wizard_line_ids.mapped('fsm_order_id')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Orders Schedule',
            'res_model': 'fsm.order',
            'domain': [('id', 'in', orders.ids)],
            'view_mode': 'tree,form',
            'view_id': False,
        }
