# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fsm_signature_capture = fields.Boolean(
        related="company_id.fsm_signature_capture",
        readonly=False,
    )
    fsm_document_signing = fields.Boolean(
        related="company_id.fsm_document_signing",
        readonly=False,
    )
    fsm_require_signature_to_complete = fields.Boolean(
        related="company_id.fsm_require_signature_to_complete",
        readonly=False,
    )
    fsm_require_document_signed_to_complete = fields.Boolean(
        related="company_id.fsm_require_document_signed_to_complete",
        readonly=False,
    )
    fsm_order_sign_oca_template_id = fields.Many2one(
        related="company_id.fsm_order_sign_oca_template_id",
        readonly=False,
    )
