# Copyright (C) 2018 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMVehicle(models.Model):
    _inherit = 'fsm.vehicle'

    inventory_location_id = fields.Many2one('stock.location',
                                            string='Inventory Location',
                                            required=True)
