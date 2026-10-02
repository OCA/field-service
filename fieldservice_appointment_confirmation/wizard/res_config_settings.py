# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fsm_appointment_reschedule_window_days = fields.Integer(
        string="Reschedule Window (days)",
        default=14,
        config_parameter="fieldservice_appointment_confirmation."
        "reschedule_window_days",
        help="Number of days ahead offered to the customer when rescheduling "
        "an appointment.",
    )
    fsm_appointment_slot_duration_hours = fields.Float(
        string="Reschedule Slot Duration (hours)",
        default=1.0,
        config_parameter="fieldservice_appointment_confirmation." "slot_duration_hours",
        help="Granularity, in hours, of the time slots offered to the customer "
        "when rescheduling an appointment.",
    )
