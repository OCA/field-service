# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AgreementPreventiveRule(models.Model):
    _name = "agreement.preventive.rule"
    _description = "Agreement Preventive Visit Rule"
    _order = "agreement_id, sequence, id"
    _rec_name = "type_id"

    agreement_id = fields.Many2one(
        "agreement", required=True, index=True, ondelete="cascade"
    )
    sequence = fields.Integer(
        default=10,
        help="For each visit type, the first rule that fits the equipment applies.",
    )
    type_id = fields.Many2one(
        "fsm.preventive.type", string="Visit Type", required=True, ondelete="restrict"
    )
    interval = fields.Integer(string="Interval (Months)", required=True, default=12)
    template_id = fields.Many2one(
        "fsm.template", string="Template", help="Work to perform during the visit."
    )

    _sql_constraints = [
        ("interval_positive", "check(interval > 0)", "The interval must be positive.")
    ]

    def _matches(self, equipment):
        """Whether the rule applies to the equipment; meant to be extended with
        the criteria that tell the equipments of an agreement apart."""
        self.ensure_one()
        return True

    def _get_template(self, equipment):
        """Template of the visits of the equipment under this rule."""
        self.ensure_one()
        return self.template_id

    @api.model_create_multi
    def create(self, vals_list):
        rules = super().create(vals_list)
        rules.agreement_id._sync_equipment_preventives()
        return rules

    def write(self, vals):
        agreements = self.agreement_id
        res = super().write(vals)
        (agreements | self.agreement_id)._sync_equipment_preventives()
        return res

    def unlink(self):
        agreements = self.agreement_id
        res = super().unlink()
        agreements._sync_equipment_preventives()
        return res
