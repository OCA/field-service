# Copyright (c) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'
    _order = "date desc"

    vehicle_id = fields.Many2one('fsm.vehicle', string="Vehicle")
    date = fields.Date(string="Date")
    company_id = fields.Many2one(
        'res.company',
        default=lambda s: s.env.user.company_id)
