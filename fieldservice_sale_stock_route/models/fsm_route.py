# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMRoute(models.Model):
    _inherit = "fsm.route"

    force_schedule = fields.Boolean(
        help="Enable this to allow scheduling on non-route days.",
    )
