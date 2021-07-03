# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMLocation(models.Model):
    _inherit = 'fsm.location'

    inventory_location_id = fields.Many2one(
        'stock.location', string='Inventory Location', required=True,
        default=lambda self: self.env.ref('stock.stock_location_customers'))
    shipping_address_id = fields.Many2one('res.partner',
                                          string='Shipping Location')

    @api.onchange('fsm_parent_id')
    def _onchange_fsm_parent_id(self):
        super(FSMLocation, self)._onchange_fsm_parent_id()
        if self.fsm_parent_id:
            self.inventory_location_id = \
                self.fsm_parent_id.inventory_location_id.id
