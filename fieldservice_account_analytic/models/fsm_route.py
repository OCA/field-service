# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMRoute(models.Model):
    _inherit = "fsm.route"

    analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Analytic Account", company_dependent=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        record = super().create(vals_list)
        for vals in vals_list:
            analytic_account = self.env["account.analytic.account"].create(
                {
                    "name": vals.get("name"),
                    "plan_id": self.env.ref(
                        "fieldservice_account_analytic.fsm_route_analytic_plan"
                    ).id,
                    "fsm_route_id": record,
                }
            )
            record.analytic_account_id = analytic_account
        return record
