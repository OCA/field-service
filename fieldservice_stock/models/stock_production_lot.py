# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    fsm_equipment_id = fields.Many2one('fsm.equipment',
                                       string='Equipment', readonly=True)
