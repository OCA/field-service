# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMRouteDayRoute(models.Model):
    _inherit = 'fsm.route.dayroute'

    dayroute_payment_ids = fields.One2many(
        'fsm.route.dayroute.payment', 'dayroute_id', string='Payment Summary')
    invoice_count = fields.Integer(
        string='Invoice Count',
        compute='_compute_invoice_count', readonly=True)

    @api.multi
    def write(self, values):
        result = super(FSMRouteDayRoute, self).write(values)
        for rec in self:
            if values.get('stage_id', False) and \
                    rec.stage_id.stage_type == 'route' and \
                    rec.stage_id.is_closed:
                for route_payment in rec.dayroute_payment_ids:
                    if route_payment.difference > 0:
                        partner = \
                            rec.person_id.partner_id.commercial_partner_id
                        account = partner.property_account_receivable_id
                        amount = route_payment.difference
                        lines = [(0, 0, {
                            'name': rec.name,
                            'account_id': account.id,
                            'partner_id': partner.id,
                            'debit': amount,
                        }), (0, 0, {
                            'name': rec.name,
                            'account_id':
                                route_payment.journal_id.
                                default_credit_account_id.id,
                            'credit': amount,
                        })]
                        route_payment.move_id = \
                            self.env['account.move'].create({
                                'journal_id': route_payment.journal_id.id,
                                'ref': rec.name,
                                'line_ids': lines,
                            })
                        route_payment.move_id.post()
        return result

    @api.depends('order_ids.invoice_count')
    def _compute_invoice_count(self):
        for dayroute in self:
            for order in dayroute.order_ids:
                dayroute.invoice_count += order.invoice_count

    @api.multi
    def action_view_invoices(self):
        action = self.env.ref(
            'account.action_invoice_tree1').read()[0]
        invoice_ids = []
        for order in self.order_ids:
            for invoice in order.invoice_ids:
                invoice_ids.append(invoice.id)
        if self.invoice_count > 1:
            action['domain'] = [('id', 'in', invoice_ids)]
        elif self.invoice_count == 1:
            action['views'] = \
                [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoice_ids[0]
        return action
