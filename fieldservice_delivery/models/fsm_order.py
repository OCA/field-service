# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    carrier_id = fields.Many2one('delivery.carrier', string="Delivery Method")
