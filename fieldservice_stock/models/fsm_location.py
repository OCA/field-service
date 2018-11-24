# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMLocation(models.Model):
    _inherit = 'fsm.location'

    inventory_location = fields.Many2one('stock.location',
                                         'Inventory Location')
