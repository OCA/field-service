# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class Inventory(models.Model):
    _inherit = 'stock.inventory'

    dayroute_id = fields.Many2one(
        'fsm.route.dayroute', string='ay Route')

    adjustment_move_id = fields.Many2one('account.move', 'Adjustment Move')

    @api.model
    def default_get(self, default):
        res = super(Inventory, self).default_get(default)
        if self._context.get('dayroute_id'):
            route_obj = self.env['fsm.route.dayroute']
            dayroute = route_obj.browse(self._context.get('dayroute_id'))
            if dayroute and dayroute.fsm_vehicle_id:
                res.update(
                    {
                        'location_id': dayroute.fsm_vehicle_id.
                        inventory_location_id.id,
                        'name': dayroute.fsm_vehicle_id.name + ' ' +
                        dayroute.date.strftime(DEFAULT_SERVER_DATE_FORMAT),
                        'dayroute_id': dayroute.id})
        return res
