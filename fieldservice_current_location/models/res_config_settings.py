# Copyright 2026 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    restrict_current_location_in_templates = fields.Boolean(
        string="Restrict Current Location in Templates",
        help=(
            "If enabled, the 'Use Current Location' button will only appear for orders "
            "based on templates that have 'Use Current Location' checked."
        ),
        config_parameter="fieldservice.restrict_current_location_in_templates",
    )
