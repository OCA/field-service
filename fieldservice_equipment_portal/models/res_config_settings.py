# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fsm_equipment_portal_public = fields.Boolean(
        string="Public Equipment Pages",
        config_parameter="fieldservice_equipment_portal.public_access",
        help="Allow anyone with an equipment page link (e.g. scanned from a "
        "printed QR code) to view the equipment page without logging in.",
    )
