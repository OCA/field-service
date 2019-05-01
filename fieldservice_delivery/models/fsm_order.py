# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    carrier_id = fields.Many2one('delivery.carrier', string="Delivery Method",
                                 compute="_compute_carrier_id")

    #Note: This function only works if the user has configured their
    #      Delivery Methods to have 'Fedex Ground', 'Fedex Standard-
    #      Overnight', and 'Fedex Priority-Overnight'
    def _compute_carrier_id(self):
        if self.priority == '0' or self.priority == '1':
            fedex = self.env['delivery.carrier'].\
                search([('name', '=', 'Fedex Ground')])
            if fedex:
                self.carrier_id = fedex
        elif self.priority == '2':
            fedex = self.env['delivery.carrier'].\
                search([('name', '=', 'Fedex Standard-Overnight')])
            if fedex:
                self.carrier_id = fedex
        elif self.priority == '3':
            fedex = self.env['delivery.carrier'].\
                search([('name', '=', 'Fedex Priority-Overnight')])
            if fedex:
                self.carrier_id = fedex
