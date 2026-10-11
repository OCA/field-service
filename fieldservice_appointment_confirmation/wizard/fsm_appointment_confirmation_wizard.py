# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FSMAppointmentConfirmationWizard(models.TransientModel):
    _name = "fsm.appointment.confirmation.wizard"
    _inherit = "mail.compose.message"
    _description = "FSM Appointment Confirmation Composer"

    attachment_ids = fields.Many2many(
        "ir.attachment",
        "fsm_appointment_confirmation_wizard_attachment_rel",
        "wizard_id",
        "attachment_id",
        string="Attachments",
    )
    partner_ids = fields.Many2many(
        "res.partner",
        "fsm_appointment_confirmation_wizard_partner_rel",
        "wizard_id",
        "partner_id",
        string="Additional Contacts",
    )

    def _action_send_mail(self, auto_commit=False):
        """Once the request email is actually sent, flag the related order
        as 'requested' (Ref: REQ-002, appointment_state)."""
        result = super()._action_send_mail(auto_commit=auto_commit)
        if self.model == "fsm.order":
            res_ids = self._evaluate_res_ids()
            if res_ids:
                self.env["fsm.order"].browse(res_ids)._mark_appointment_requested()
        return result
