# Copyright (C) 2025, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMStage(models.Model):
    _inherit = "fsm.stage"

    portal_visible = fields.Boolean(
        string="Visible in Portal",
        default=True,
        help="Enable to display field service orders based on it's stage in the portal",
    )
