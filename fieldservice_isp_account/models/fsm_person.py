# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMPerson(models.Model):
    _inherit = 'fsm.person'

    bill_count = fields.Integer(string='Vendor Bills',
                                compute='_compute_vendor_bills')

    def _compute_vendor_bills(self):
        self.bill_count = self.env['account.invoice'].search_count([
            ('partner_id', '=', self.partner_id.id)])

    @api.multi
    def action_view_bills(self):
        for bill in self:
            action = self.env.ref('account.action_invoice_tree1').read()[0]
            vendor_bills = self.env['account.invoice'].search(
                [('partner_id', '=', bill.partner_id.id)])
            if len(vendor_bills) == 1:
                action['views'] = [
                    (self.env.ref('account.invoice_form').id, 'form')]
                action['res_id'] = vendor_bills.id
            else:
                action['domain'] = [('id', 'in', vendor_bills.ids)]
            return action
