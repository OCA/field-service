# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockRequest(models.Model):
    _inherit = 'stock.request'

    @api.multi
    def action_assign(self):
        for rec in self:
            for move in rec.move_ids:
                if move.picking_id.picking_type_id == self.env.ref(
                        'fieldservice_vehicle_stock.'
                        'picking_type_vehicle_to_location'):
                    return move.picking_id.action_assign()

    @api.multi
    def action_deliver(self):
        for rec in self:
            for move in rec.move_ids:
                if move.picking_id.picking_type_id == self.env.ref(
                        'fieldservice_vehicle_stock.'
                        'picking_type_vehicle_to_location'):
                    return move.picking_id.action_done()

    def action_show_details(self):
        for move in self.move_ids:
            if move.picking_id.picking_type_id == self.env.ref(
                    'fieldservice_vehicle_stock.'
                    'picking_type_vehicle_to_location'):
                return move.action_show_details()
