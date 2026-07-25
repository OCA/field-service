# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    fsm_signature_capture = fields.Boolean(
        related="company_id.fsm_signature_capture",
    )
    fsm_document_signing = fields.Boolean(
        related="company_id.fsm_document_signing",
    )
    sign_request_ids = fields.One2many(
        comodel_name="sign.oca.request",
        inverse_name="fsm_order_id",
        string="Signature Requests",
    )
    sign_request_count = fields.Integer(
        compute="_compute_sign_request_count",
        compute_sudo=True,
    )
    sign_request_id = fields.Many2one(
        comodel_name="sign.oca.request",
        string="Signature Request",
        compute="_compute_sign_request_id",
        compute_sudo=True,
        store=True,
    )
    sign_request_state = fields.Selection(
        related="sign_request_id.state",
        string="Signature Request Status",
    )

    @api.depends("sign_request_ids")
    def _compute_sign_request_count(self):
        for order in self:
            order.sign_request_count = len(order.sign_request_ids)

    @api.depends("sign_request_ids", "sign_request_ids.state")
    def _compute_sign_request_id(self):
        for order in self:
            order.sign_request_id = order.sign_request_ids.sorted("id", reverse=True)[
                :1
            ]

    def action_view_sign_requests(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "sign_oca.sign_oca_request_act_window"
        )
        action["domain"] = [("id", "in", self.sign_request_ids.ids)]
        action["context"] = dict(
            self.env.context,
            default_record_ref=f"{self._name},{self.id}",
        )
        return action

    def action_request_document_signature(self):
        self.ensure_one()
        if not self.company_id.fsm_document_signing:
            raise UserError(
                self.env._(
                    "Document signing is disabled for company %(company)s.",
                    company=self.company_id.display_name,
                )
            )
        template = self.company_id.fsm_order_sign_oca_template_id
        if not template:
            raise UserError(
                self.env._(
                    "Configure an FSM Order Sign Template on the company "
                    "before requesting a document signature."
                )
            )
        request = (
            self.env["sign.oca.request"]
            .sudo()
            .create(template._prepare_sign_oca_request_vals_from_record(self))
        )
        request.action_send()
        return self.action_view_sign_requests()

    def _check_signature_requirements_before_complete(self):
        for order in self:
            company = order.company_id
            if (
                company.fsm_signature_capture
                and company.fsm_require_signature_to_complete
                and not order.signature
            ):
                raise UserError(
                    self.env._(
                        "Customer signature is required before completing "
                        "order %(order)s.",
                        order=order.display_name,
                    )
                )
            if (
                company.fsm_document_signing
                and company.fsm_require_document_signed_to_complete
                and not order.sign_request_ids.filtered(lambda r: r.state == "2_signed")
            ):
                raise UserError(
                    self.env._(
                        "A signed document is required before completing "
                        "order %(order)s.",
                        order=order.display_name,
                    )
                )

    def action_complete(self):
        self._check_signature_requirements_before_complete()
        return super().action_complete()
