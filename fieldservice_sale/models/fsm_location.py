# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMLocation(models.Model):
    _inherit = 'fsm.location'

    sales_territory_id = fields.Many2one('fsm.territory',
                                         string='Sales Territory')
    sale_order_count = fields.Integer(compute='_compute_sale_order_count',
                                      string='Sales')

    @api.multi
    def _compute_sale_order_count(self):
        for location in self:
            location.sale_order_count = self.env['sale.order'].search_count(
                [('fsm_location_id', '=', location.id)])
