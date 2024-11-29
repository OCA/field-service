# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


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
            print("\n\n", record.analytic_account_id, "\n\n")
        return record

    def action_view_analytic_account(self):
        self.ensure_one()
        analytic_account = self.env["account.analytic.account"].search(
            [("fsm_route_id", "=", self.id)], limit=1
        )

        if analytic_account:
            return {
                "type": "ir.actions.act_window",
                "res_model": "account.analytic.account",
                "view_mode": "form",
                "res_id": analytic_account.id,
                "name": _("Analytic Account for Route %s") % self.name,
            }
