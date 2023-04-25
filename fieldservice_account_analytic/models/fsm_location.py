# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Analytic Account", company_dependent=True
    )

    @api.model
    def get_default_customer(self):
        if self.fsm_parent_id:
            return self.fsm_parent_id.customer_id.id
        return self.owner_id.id

    customer_id = fields.Many2one(
        "res.partner",
        string="Billed Customer",
        required=True,
        ondelete="restrict",
        auto_join=True,
        tracking=True,
        default=get_default_customer,
    )

    @api.onchange("fsm_parent_id")
    def _onchange_fsm_parent_id_account(self):
        self.customer_id = self.fsm_parent_id.customer_id or False
