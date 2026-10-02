# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FSMRecurring(models.Model):
    _inherit = "fsm.recurring"

    preventive_agreement_id = fields.Many2one(
        "agreement",
        string="Preventive Agreement",
        help="Only the equipments of this agreement go in the preventive visits.",
    )

    preventive_agreement_required = fields.Boolean(
        related="company_id.preventive_agreement_required"
    )
    preventive_available_agreement_ids = fields.Many2many(
        "agreement", compute="_compute_preventive_available_agreement_ids"
    )

    @api.depends("is_preventive", "location_id", "company_id")
    def _compute_preventive_available_agreement_ids(self):
        """Agreements of the equipments the visit can cover."""
        for recurring in self:
            if not (recurring.is_preventive and recurring.location_id):
                recurring.preventive_available_agreement_ids = False
                continue
            domain = [
                leaf
                for leaf in recurring._get_preventive_equipment_domain()
                if leaf[0] != "agreement_id"
            ]
            groups = self.env["fsm.equipment"]._read_group(
                domain
                + [("agreement_id", "!=", False), ("preventive_ids", "!=", False)],
                ["agreement_id"],
            )
            recurring.preventive_available_agreement_ids = self.env["agreement"].union(
                *(agreement for (agreement,) in groups)
            )

    @api.constrains("is_preventive", "preventive_agreement_id", "company_id")
    def _check_preventive_agreement_required(self):
        for recurring in self:
            if (
                recurring.is_preventive
                and recurring.preventive_agreement_required
                and not recurring.preventive_agreement_id
            ):
                raise ValidationError(
                    _(
                        "The preventive visit %(name)s needs an agreement.",
                        name=recurring.display_name,
                    )
                )

    @api.onchange("location_id", "is_preventive")
    def _onchange_preventive_agreement_location(self):
        """Preselect the agreement when the location leaves no choice; the user
        can still empty the field to cover every equipment."""
        available = self.preventive_available_agreement_ids
        if self.preventive_agreement_id not in available:
            self.preventive_agreement_id = False
        if not self.preventive_agreement_id and len(available) == 1:
            self.preventive_agreement_id = available

    @api.depends("preventive_agreement_id")
    def _compute_preventive_equipment_count(self):
        return super()._compute_preventive_equipment_count()

    def _get_preventive_equipment_domain(self):
        domain = super()._get_preventive_equipment_domain()
        if self.preventive_agreement_id:
            domain.append(("agreement_id", "=", self.preventive_agreement_id.id))
        return domain

    def _prepare_order_values(self, date=None):
        vals = super()._prepare_order_values(date=date)
        if self.is_preventive and self.preventive_agreement_id:
            vals["agreement_id"] = self.preventive_agreement_id.id
        return vals
