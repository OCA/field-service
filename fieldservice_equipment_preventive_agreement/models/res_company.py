# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    preventive_agreement_required = fields.Boolean(
        string="Require Agreement on Preventive Visits",
        help="Preventive visits cannot be saved without an agreement.",
    )
