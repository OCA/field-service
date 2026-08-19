# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    agreement_ids = fields.One2many("agreement", "partner_id", string="Agreements")
    agreements_count = fields.Integer(compute="_compute_agreements_count")

    @api.depends("agreement_ids")
    def _compute_agreements_count(self):
        results = self.env["agreement"]._read_group(
            [("partner_id", "in", self.ids)],
            ["partner_id"],
            ["__count"],
        )
        agreement_dict = {partner.id: count for partner, count in results}
        for rec in self:
            rec.agreements_count = agreement_dict.get(rec.id, 0)

    def action_open_agreement(self):
        self.ensure_one()
        action = self.env.ref("agreement.agreement_action")
        result = action.read()[0]
        result.update(
            {
                "domain": [("partner_id", "=", self.id)],
                "context": {"default_partner_id": self.id},
            }
        )
        return result
