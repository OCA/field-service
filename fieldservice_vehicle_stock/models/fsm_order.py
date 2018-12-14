# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class FSMOrderLine(models.Model):
    _inherit = 'fsm.order.line'

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        values = super(self, FSMOrderLine).\
            _prepare_procurement_values(group_id)
        values.update({'route_ids': self.env.ref(
            'fieldservice_vehicle_stock.route_stock_to_vehicle_to_location')
        })
        return values
