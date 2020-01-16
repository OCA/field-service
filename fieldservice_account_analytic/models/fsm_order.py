# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    total_cost = fields.Float(compute='_compute_total_cost',
                              string='Total Cost')
    bill_to = fields.Selection([('location', 'Bill Location'),
                                ('contact', 'Bill Contact')],
                               string="Bill to",
                               required=True,
                               default="location")
    customer_id = fields.Many2one('res.partner', string='Contact',
                                  domain=[('customer', '=', True)],
                                  change_default=True,
                                  index=True,
                                  track_visibility='always')

    def _compute_total_cost(self):
        """ To be overridden as needed from other modules """
        for order in self:
            order.total_cost = 0.0

    @api.onchange('location_id', 'customer_id')
    def _onchange_location_id_customer_account(self):
        if self.env.user.company_id.fsm_filter_location_by_contact:
            if self.location_id:
                return {'domain': {'customer_id': [('service_location_id', '=',
                                                    self.location_id.id)]}}
            else:
                return {'domain': {'customer_id': [],
                                   'location_id': []}}
        else:
            if self.customer_id:
                return {'domain': {'location_id': [('partner_id', '=',
                                                    self.customer_id.id)]}}
            else:
                return {'domain': {'location_id': [],
                                   'customer_id': []}}

    @api.onchange('customer_id')
    def _onchange_customer_id_location(self):
        if self.customer_id:
            self.location_id = self.customer_id.service_location_id

    @api.multi
    def write(self, vals):
        res = super(FSMOrder, self).write(vals)
        for order in self:
            if 'customer_id' not in vals and order.customer_id is False:
                order.customer_id = order.location_id.customer_id.id
        return res
