# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    auto_validate_pickings = fields.Boolean(
        string="Auto Validate FSM Pickings",
        config_parameter="fieldservice_stock.auto_validate_pickings",
        help="If enabled, related stock pickings will be automatically "
        "validated when an FSM order is completed.",
    )
