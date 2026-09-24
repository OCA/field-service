# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    preventive_agreement_required = fields.Boolean(
        related="company_id.preventive_agreement_required", readonly=False
    )
