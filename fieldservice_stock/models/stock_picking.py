# Copyright (C) 2018 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fsm_order_id = fields.Many2one(related="group_id.fsm_order_id",
                                   string="Field Service Order", store=True)

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if vals.get('fsm_order_id'):
            res.fsm_order_id = vals.get('fsm_order_id')
        return res
