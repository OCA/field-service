# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def post(self):
        res = super().post()
        dayroute_payment_obj = self.env['fsm.route.dayroute.payment']
        for rec in self:
            for fsm_order_rec in rec.fsm_order_ids:
                if fsm_order_rec.dayroute_id:
                    dayroute_payment = dayroute_payment_obj.search([
                        ('journal_id', '=', rec.journal_id.id),
                        ('dayroute_id', '=',
                         fsm_order_rec.dayroute_id.id)
                    ])
                    if not dayroute_payment:
                        dayroute_payment_obj.create({
                            'journal_id': self.journal_id.id,
                            'dayroute_id': fsm_order_rec.dayroute_id.id
                        })
        return res
