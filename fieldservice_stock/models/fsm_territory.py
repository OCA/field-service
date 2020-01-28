# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FSMTerritory(models.Model):
    _inherit = 'fsm.territory'

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
