# Copyright (C) 2025, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMStage(models.Model):
    _inherit = "fsm.stage"

    name = fields.Char(translate=True)

    notification_event = fields.Selection(
        [
            ("none", "None"),
            ("started", "Work Started"),
            ("completed", "Work Completed"),
        ],
        default="none",
        required=True,
        help="Customer notification triggered when an order enters this stage.",
    )

    portal_visible = fields.Boolean(
        string="Visible in Portal",
        default=True,
        help="Enable to display field service orders based on their stage in the portal.",
    )
