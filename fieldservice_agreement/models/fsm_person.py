# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMPerson(models.Model):
    _inherit = "fsm.person"

    agreement_count = fields.Integer(
        string="# of Agreements", compute="_compute_agreements"
    )

    def _compute_agreements(self):
        self.agreement_count = self.env["agreement"].search_count(
            [("partner_id", "=", self.name)]
        )

    def action_view_agreements(self):
        for person in self:
            action = self.env.ref(
                "agreement_legal.agreement_operations_agreement"
            ).read()[0]
            agreements = self.env["agreement"].search(
                [("partner_id", "=", person.partner_id.id)]
            )
            if len(agreements) == 1:
                action["views"] = [
                    (
                        self.env.ref("agreement_legal.partner_agreement_form_view").id,
                        "form",
                    )
                ]
                action["res_id"] = agreements.id
            else:
                action["domain"] = [("id", "in", agreements.ids)]
            return action
