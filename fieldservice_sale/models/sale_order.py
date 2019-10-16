# Copyright (C) 2019 Brian McMaster
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fsm_location_id = fields.Many2one(
        'fsm.location', string='Service Location',
        help="SO Lines generating a FSM order will be for this location")
    date_fsm_request = fields.Datetime(
        string='Requested Service Date', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        copy=False, default=fields.Datetime.now)
    fsm_order_ids = fields.Many2many(
        'fsm.order', compute='_compute_fsm_order_ids',
        string='Field Service orders associated to this sale')
    fsm_order_count = fields.Float(
        string='Field Service Orders', compute='_compute_fsm_order_ids')

    @api.multi
    @api.depends('order_line.product_id')
    def _compute_fsm_order_ids(self):
        for order in self:
            order.fsm_order_ids = self.env['fsm.order'].search([
                ('sale_line_id', 'in', order.order_line.ids)])
            order.fsm_order_count = len(order.fsm_order_ids)

    @api.multi
    def action_confirm(self):
        """ On SO confirmation, some lines generate field service orders. """
        result = super(SaleOrder, self).action_confirm()
        self.order_line._field_service_generation()
        return result

    @api.multi
    def action_view_fsm_order(self):
        fsm_orders = self.mapped('fsm_order_ids')
        action = self.env.ref('fieldservice.action_fsm_dash_order').read()[0]
        if len(fsm_orders) > 1:
            action['domain'] = [('id', 'in', fsm_orders.ids)]
        elif len(fsm_orders) == 1:
            action['views'] = [(self.env.
                                ref('fieldservice.fsm_order_form').id,
                                'form')]
            action['res_id'] = fsm_orders.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
