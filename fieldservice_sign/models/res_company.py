# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    fsm_signature_capture = fields.Boolean(
        string="FSM Signature Capture",
        help="Enable on-site customer signature capture on Field Service orders.",
    )
    fsm_document_signing = fields.Boolean(
        string="FSM Document Signing",
        help="Enable sign_oca document signing on Field Service orders.",
    )
    fsm_require_signature_to_complete = fields.Boolean(
        string="Require Signature to Complete",
        help="Block completing an order until a customer signature is captured.",
    )
    fsm_require_document_signed_to_complete = fields.Boolean(
        string="Require Document Signed to Complete",
        help="Block completing an order until a linked signature request is signed.",
    )
    fsm_order_sign_oca_template_id = fields.Many2one(
        comodel_name="sign.oca.template",
        string="FSM Order Sign Template",
        domain="[('model_id.model', '=', 'fsm.order')]",
        help="Default sign_oca template used when requesting a document signature.",
    )
