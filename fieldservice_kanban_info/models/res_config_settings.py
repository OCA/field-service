# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    schedule_time_range_format = fields.Selection(
        selection=[
            ("time_only", "Time Range Only (e.g., 15:30 - 17:00)"),
            ("date_and_time", "Date and Time Range (e.g., 19/02/2025 15:30 - 17:00)"),
        ],
        config_parameter="fieldservice.schedule_time_range_format",
        default="time_only",
        required=True,
    )
