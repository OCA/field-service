# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockRequest(models.Model):
    _inherit = 'stock.request'

    @api.model
    def create(self, vals):
        if 'fsm_order_id' in vals and vals.get('fsm_order_id'):
            fsm_order = self.env['fsm.order'].browse(vals.get('fsm_order_id'))
            vals.update({
                'analytic_account_id':
                    fsm_order.location_id.analytic_account_id.id
            })
        return super().create(vals)
