# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMRoutePayment(models.Model):
    _name = 'fsm.route.dayroute.payment'
    _rec_name = 'journal_id'
    _description = 'Field Service Route Dayroute Payment Check and Reconcile'

    journal_id = fields.Many2one('account.journal', string='Journal')
    amount_collected = fields.Float(
        string='Collected Amount', readonly=True,
        compute='_compute_amout_collected')
    amount_counted = fields.Float(
        string='Counted Amount', compute='_compute_amout_collected',
        default=0.0)
    difference = fields.Float(
        string='Difference', compute='_compute_amout_collected')
    move_id = fields.Many2one('account.move', string='Journal Entry')
    dayroute_id = fields.Many2one('fsm.route.dayroute', string='Day Route')

    def _compute_amout(self):
        pass
