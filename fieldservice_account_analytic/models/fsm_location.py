# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class FSMLocation(models.Model):
    _inherit = 'fsm.location'

    analytic_account_id = fields.Many2one('account.analytic.account',
                                          string='Analytic Account',
                                          company_dependent=True)

    customer_id = fields.Many2one(
        'res.partner', string='Billed Customer', required=True,
        ondelete='restrict', auto_join=True, track_visibility='onchange')

    @api.onchange('fsm_parent_id')
    def _onchange_fsm_parent_id_account(self):
        self.customer_id = self.fsm_parent_id.customer_id or False
