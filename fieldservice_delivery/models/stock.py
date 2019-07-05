# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    carrier_id = fields.Many2one('delivery.carrier', string="Delivery Method")
