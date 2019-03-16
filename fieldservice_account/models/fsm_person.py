# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMPerson(models.Model):
    _inherit = 'fsm.person'

    bill_count = fields.Integer(string='Vendor Bills',
                                compute='_compute_vendor_bills')

    def _compute_vendor_bills(self):
        count = 0
        bills = self.env['account.invoice'].search([])
        for bill in bills:
            if bill.partner_id == self.partner_id:
                count += 1
        self.bill_count = count

    @api.multi
    def action_view_bills(self):
        for bill in self:
            action = self.env.ref('account.action_invoice_tree2').read()[0]
            vendor_bills = self.env['account.invoice'].search(
                [('partner_id', '=', bill.name)])
            if len(vendor_bills) == 0 or len(vendor_bills) > 1:
                action['domain'] = [('id', 'in', vendor_bills.ids)]
            elif vendor_bills:
                action['views'] = [
                    (self.env.ref('account.invoice_supplier_form').id, 'form')]
                action['res_id'] = vendor_bills.id
            return action
