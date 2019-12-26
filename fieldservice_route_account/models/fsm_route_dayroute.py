# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMRouteDayRoute(models.Model):
    _inherit = 'fsm.route.dayroute'

    dayroute_payment_ids = fields.One2many(
        'fsm.route.dayroute.payment', 'dayroute_id', string='Payment Summary')

    @api.multi
    def write(self, values):
        result = super(FSMRouteDayRoute, self).write(values)
        for record in self:
            if record.stage_id.stage_type == 'route' and\
                    record.stage_id.is_closed:
                for route_payment in record.dayroute_payment_ids:
                    if route_payment.difference > 0:
                        route_payment.move_id = \
                            self.env['account.move'].create({
                                'journal_id': route_payment.journal_id.id,
                                'line_ids': [
                                    (0, 0, {
                                        'account_id': record.person_id.
                                     partner_id.
                                     property_account_receivable_id.id,
                                        'partner_id': record.
                                     person_id.partner_id.id,
                                        'debit': route_payment.difference}),
                                    (0, 0, {
                                        'account_id': route_payment.
                                     journal_id.default_credit_account_id.id,
                                        'credit': route_payment.difference})]
                            })
                        route_payment.move_id.action_post()
        return result
