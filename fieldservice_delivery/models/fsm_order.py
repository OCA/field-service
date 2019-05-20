# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    carrier_id = fields.Many2one('delivery.carrier', string="Delivery Method",
                                 compute="_compute_carrier_id")

    """ Note: This function only works if the user has configured their
        Delivery Methods to have 'Fedex Ground', 'Fedex Standard-
        Overnight', and 'Fedex Priority-Overnight'"""
    def _compute_carrier_id(self):
        carrier_obj = self.env['delivery.carrier']
        for rec in self:
            if rec.priority == '0' or rec.priority == '1':
                fedex = carrier_obj.search(
                    [('name', '=', 'Fedex Ground')])
                if fedex:
                    rec.carrier_id = fedex
            elif rec.priority == '2':
                fedex = carrier_obj.search(
                    [('name', '=', 'Fedex Standard-Overnight')])
                if fedex:
                    rec.carrier_id = fedex
            elif rec.priority == '3':
                fedex = carrier_obj.search(
                    [('name', '=', 'Fedex Priority-Overnight')])
                if fedex:
                    rec.carrier_id = fedex
