# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Agreement(models.Model):
    _inherit = "agreement"

    preventive_rule_ids = fields.One2many(
        "agreement.preventive.rule", "agreement_id", string="Preventive Visits"
    )

    def _sync_equipment_preventives(self):
        self.env["fsm.equipment"].search(
            [("agreement_id", "in", self.ids)]
        )._sync_agreement_preventives()
