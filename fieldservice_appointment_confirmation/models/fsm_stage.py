# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FSMStage(models.Model):
    _inherit = "fsm.stage"

    allow_confirmation_request = fields.Boolean(
        string="Allow Appointment Confirmation Request",
        default=False,
        help="If enabled, field service orders in this stage display the "
        "button to request an appointment confirmation from the customer.",
    )
