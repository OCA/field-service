# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMPerson(models.Model):
    _inherit = "fsm.person"

    agreement_count = fields.Integer(
        string="# of Agreements",
        compute="_compute_agreement_count",
    )

    def _compute_agreement_count(self):
        data = self.env["agreement"]._read_group(
            [("partner_id", "in", self.partner_id.ids)],
            ["partner_id"],
            ["__count"],
        )
        counts = {rec.id: count for rec, count in data}
        for rec in self:
            rec.agreement_count = counts.get(rec.partner_id.id, 0)

    def action_view_agreements(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "agreement.agreement_action"
        )
        records = self.env["agreement"].search(
            [("partner_id", "in", self.partner_id.ids)]
        )
        if len(records) == 1:
            action["views"] = [(self.env.ref("agreement.agreement_form").id, "form")]
            action["res_id"] = records.id
        else:
            action["domain"] = [("id", "in", records.ids)]
        return action
